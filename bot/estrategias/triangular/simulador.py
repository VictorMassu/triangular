from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from time import sleep

from bot.estrategias.triangular.calcular_rota import calcular_rota
from bot.estrategias.triangular.avaliador import aplicar_taxa, buscar_preco_com_profundidade
from bot.config import (
    VALOR_INICIAL, MOEDA_BASE, LUCRO_MINIMO, VOLUME_MINIMO_PARA_ANALISE,
    TOP_MOEDAS, MOEDAS_BLACKLIST, MAX_WORKERS
)
from logs.logs_core.logger import log

buscar_fn = buscar_preco_com_profundidade
rodando = True

def construir_par(m1, m2, todos_pares):
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None

def gerar_ticker_dict(pares_raw):
    ticker_dict = {}
    for p in pares_raw:
        try:
            ask = float(p.get('ask', 0))
            bid = float(p.get('bid', 0))
            if ask <= 0 or bid <= 0:
                log.debug("Preço inválido encontrado", categoria="preco_zero", dados=p, id=p.get("symbol"))
                continue
            ticker_dict[p['symbol']] = p
        except Exception:
            log.erro("Erro ao processar par", categoria="preco_parse_fail", dados=p, id=p.get("symbol"))
    return ticker_dict

def filtrar_moedas_com_base(todos_pares):
    moedas = set()
    for par in todos_pares:
        if par.startswith(MOEDA_BASE):
            moedas.add(par[len(MOEDA_BASE):])
        elif par.endswith(MOEDA_BASE):
            moedas.add(par[:-len(MOEDA_BASE)])
    return sorted([
        m for m in moedas
        if not any(x in m for x in MOEDAS_BLACKLIST) and not any(y in m for y in ['UP', 'DOWN'])
    ])[:TOP_MOEDAS]

def gerar_rotas(moedas_filtradas, todos_pares):
    rotas = []
    for m1 in moedas_filtradas:
        for m2 in moedas_filtradas:
            if m1 != m2 and construir_par(m1, m2, todos_pares):
                rotas.append((m1, m2))
    return rotas

def analisar_rota(exchange, m1, m2, ticker_dict, todos_pares):
    if not rodando:
        return

    try:
        par1 = construir_par(MOEDA_BASE, m1, todos_pares)
        par2 = construir_par(m1, m2, todos_pares)
        par3 = construir_par(m2, MOEDA_BASE, todos_pares)

        if not (par1 and par2 and par3):
            return

        log.debug("🔄 Simulando rota", categoria="rota_start", dados={"par1": par1, "par2": par2, "par3": par3})

        resultado = calcular_rota(
            moeda_base=MOEDA_BASE,
            m1=m1,
            m2=m2,
            ticker_dict=ticker_dict,
            todos_pares=todos_pares,
            capital_inicial=VALOR_INICIAL,
            aplicar_taxa_fn=aplicar_taxa,
            buscar_preco_fn=buscar_fn,
            exchange_obj=exchange
        )

        rota_id = resultado.get("rota_id") if resultado else f"{MOEDA_BASE}_{m1}_{m2}_{MOEDA_BASE}"

        if resultado:
            log.debug("Rota simulada com sucesso", categoria="rota_ok", dados=resultado, id=rota_id)
            print(f"[DEBUG] 📎 Salvando rota: {rota_id}")
            log.salvar_rota(resultado)

            if resultado["lucro_percentual"] >= LUCRO_MINIMO * 100:
                log.oportunidade(resultado)

            if resultado["lucro_percentual"] < -1.0:
                log.debug("Lucro muito negativo (< -1%)", categoria="lucro_negativo", dados=resultado, id=rota_id)

            if resultado["valor_final"] < resultado["valor_inicial"] * 0.95:
                log.debug("Valor final < 95% do inicial", categoria="valor_baixo", dados=resultado, id=rota_id)

            if any([resultado["vol1"] < 1000, resultado["vol2"] < 1000, resultado["vol3"] < 1000]):
                log.debug("Volume muito baixo", categoria="volume_baixo", dados=resultado, id=rota_id)

            if any([resultado["preco1"] is None, resultado["preco2"] is None, resultado["preco3"] is None]):
                log.debug("Preço None detectado", categoria="preco_none", dados=resultado, id=rota_id)

            if -0.01 <= resultado["lucro_percentual"] <= 0.01:
                log.debug("Lucro neutro (entre -0.01% e 0.01%)", categoria="lucro_neutro", dados=resultado, id=rota_id)

        else:
            log.debug("Resultado None na simulação da rota", categoria="rota_nula", dados={
                "moeda_base": MOEDA_BASE,
                "m1": m1,
                "m2": m2,
                "par1": par1,
                "par2": par2,
                "par3": par3,
                "timestamp": datetime.now().isoformat()
            }, id=rota_id)
    except Exception as e:
        log.erro("Erro ao analisar rota", categoria="rota_excecao", dados={"erro": str(e), "moedas": [m1, m2]})

def simular_rotas(exchange, volume_minimo=VOLUME_MINIMO_PARA_ANALISE):
    try:
        log.info("Iniciando simulação paralela de rotas", categoria="simulador", dados={"exchange": exchange.get_nome()})
        pares_raw = exchange.filtrar_pares_por_volume(volume_minimo)
        log.info("Pares filtrados com sucesso", categoria="simulador", dados={"qtd_pares": len(pares_raw)})

        ticker_dict = gerar_ticker_dict(pares_raw)
        todos_pares = set(ticker_dict.keys())

        moedas_filtradas = filtrar_moedas_com_base(todos_pares)
        log.info("Moedas com base filtradas", categoria="simulador", dados={"quantidade": len(moedas_filtradas)})

        rotas_validas = gerar_rotas(moedas_filtradas, todos_pares)
        log.info("Rotas válidas geradas", categoria="simulador", dados={"quantidade": len(rotas_validas)})

        batch_size = MAX_WORKERS
        delay = 1.5

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for i in range(0, len(rotas_validas), batch_size):
                lote = rotas_validas[i:i + batch_size]
                log.debug("Processando lote de rotas", categoria="batch", dados={"inicio": i, "fim": i + batch_size})

                futures = [
                    executor.submit(analisar_rota, exchange, m1, m2, ticker_dict, todos_pares)
                    for m1, m2 in lote
                ]

                for future in as_completed(futures):
                    if not rodando:
                        break
                    try:
                        future.result(timeout=20)
                    except TimeoutError:
                        log.erro("Thread expirou no lote", categoria="batch_timeout")
                    except Exception as e:
                        log.erro("Erro no lote de análise", categoria="batch_erro", dados={"erro": str(e)})

                sleep(delay)

    except Exception as e:
        log.erro("Erro geral na simulação de rotas", categoria="simulador_erro", dados={"erro": str(e)})
