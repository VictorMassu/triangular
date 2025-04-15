import itertools
from bot_triangular.analisador.calcular_rota import calcular_rota
from logs.logs_agent.logger_console import log_info
from logs.logs_agent.logger_debug import log_debug_json
from bot_triangular.analisador.avaliador import aplicar_taxa, buscar_preco_ticker
from bot_triangular.config import (
    VALOR_INICIAL, MOEDA_BASE, LUCRO_MINIMO, LOG_ROTAS, LOG_OPORTUNIDADES,
    VOLUME_MINIMO_PARA_ANALISE, VALOR_MINIMO_MOEDA,
    TOP_MOEDAS, MOEDAS_BLACKLIST
)
from logs.logs_core.logger_json import salvar_json_lista
from datetime import datetime

log_debug_json("⚠️ Teste de debug manual", "teste_manual", {"exemplo": 123})

def simular_rotas(exchange, volume_minimo=VOLUME_MINIMO_PARA_ANALISE):
    pares_raw = exchange.filtrar_pares_por_volume(volume_minimo)
    log_info(f"🔍 {len(pares_raw)} pares com volume > {volume_minimo}")

    ticker_dict = {}
    for p in pares_raw:
        try:
            ask = float(p.get('ask', 0))
            bid = float(p.get('bid', 0))
            if ask <= 0 or bid <= 0:
                log_debug_json(f"[PREÇO] Preço inválido para {p['symbol']} (ask: {ask}, bid: {bid})",
                               categoria="preco_zero", dados=p, id=p.get("symbol"), silencioso=True)
                continue
            ticker_dict[p['symbol']] = p
        except Exception as e:
            log_debug_json(f"Erro ao processar par: {str(e)}",
                           categoria="preco_parse_fail", dados=p, id=p.get("symbol"))

    todos_pares = set(ticker_dict.keys())

    moedas_com_usdt = set()
    for par in todos_pares:
        if par.startswith(MOEDA_BASE):
            moedas_com_usdt.add(par[len(MOEDA_BASE):])
        elif par.endswith(MOEDA_BASE):
            moedas_com_usdt.add(par[:-len(MOEDA_BASE)])

    moedas_filtradas = sorted([
        m for m in moedas_com_usdt
        if not any(x in m for x in MOEDAS_BLACKLIST) and not any(y in m for y in ['UP', 'DOWN'])
    ])[:TOP_MOEDAS]

    log_info(f"🔎 {len(moedas_filtradas)} moedas com pares {MOEDA_BASE} analisadas (TOP {TOP_MOEDAS})")

    rotas_validas = []
    for m1 in moedas_filtradas:
        for m2 in moedas_filtradas:
            if m1 != m2 and construir_par(m1, m2, todos_pares):
                rotas_validas.append((m1, m2))

    log_info(f"🔁 {len(rotas_validas)} rotas triangulares válidas encontradas")

    for m1, m2 in rotas_validas:
        try:
            par1 = construir_par(MOEDA_BASE, m1, todos_pares)
            par2 = construir_par(m1, m2, todos_pares)
            par3 = construir_par(m2, MOEDA_BASE, todos_pares)

            if not (par1 and par2 and par3):
                continue

            resultado = calcular_rota(
                moeda_base=MOEDA_BASE,
                m1=m1,
                m2=m2,
                ticker_dict=ticker_dict,
                todos_pares=todos_pares,
                capital_inicial=VALOR_INICIAL,
                aplicar_taxa_fn=aplicar_taxa,
                buscar_preco_fn=buscar_preco_ticker,
            )

            rota_id = resultado.get("rota_id") if resultado else f"{MOEDA_BASE}_{m1}_{m2}_{MOEDA_BASE}"

            if resultado:
                print(f"\n[DEBUG] ✅ Rota ID: {rota_id}")
                print(f"[DEBUG] 💸 Lucro: {resultado['lucro_percentual']:.4f}% | Lucro sem taxa: {resultado['lucro_sem_taxa']:.4f}% | Spread total: {resultado['spread_total']:.6f}")
                salvar_json_lista(LOG_ROTAS, resultado)

                if resultado["lucro_percentual"] >= LUCRO_MINIMO * 100:
                    salvar_json_lista(LOG_OPORTUNIDADES, resultado)

                if resultado["lucro_percentual"] < -1.0:
                    log_debug_json("Lucro muito negativo (< -1%) detectado", "lucro_negativo", resultado, id=rota_id)

                if resultado["valor_final"] < resultado["valor_inicial"] * 0.95:
                    log_debug_json("Valor final abaixo de 95% do inicial", "valor_baixo", resultado, id=rota_id)

                if any([resultado["vol1"] < 1000, resultado["vol2"] < 1000, resultado["vol3"] < 1000]):
                    log_debug_json("Volume muito baixo em uma das etapas", "volume_baixo", resultado, id=rota_id)

                if any([resultado["preco1"] is None, resultado["preco2"] is None, resultado["preco3"] is None]):
                    log_debug_json("Preço None detectado mesmo sem exceção", "preco_none", resultado, id=rota_id)

                if -0.01 <= resultado["lucro_percentual"] <= 0.01:
                    log_debug_json("Lucro neutro (entre -0.01% e 0.01%)", "lucro_neutro", resultado, id=rota_id)

            else:
                log_debug_json("Resultado None ao simular rota",
                               categoria="rota_nula",
                               dados={
                                   "moeda_base": MOEDA_BASE,
                                   "m1": m1,
                                   "m2": m2,
                                   "par1": par1,
                                   "par2": par2,
                                   "par3": par3,
                                   "timestamp": datetime.now().isoformat()
                               },
                               id=rota_id)

        except Exception as e:
            log_debug_json(
                mensagem=f"Erro ao simular rota {m1}-{m2}: {str(e)}",
                categoria="simulador",
                dados={
                    "moeda_base": MOEDA_BASE,
                    "m1": m1,
                    "m2": m2,
                    "par1": par1 if 'par1' in locals() else None,
                    "par2": par2 if 'par2' in locals() else None,
                    "par3": par3 if 'par3' in locals() else None
                },
                id=f"{MOEDA_BASE}_{m1}_{m2}_{MOEDA_BASE}"
            )

def construir_par(m1, m2, todos_pares):
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None
