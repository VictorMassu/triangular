from datetime import datetime
from time import time
import threading
from logs.logs_core.logger import log
from bot.config import LUCRO_IRREALISTA


def timeout_fn(fn, timeout, *args, **kwargs):
    result = [None]
    def target():
        try:
            result[0] = fn(*args, **kwargs)
        except Exception as e:
            result.append(e)
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TimeoutError("⏰ Timeout ao buscar preço com profundidade")
    if len(result) == 2 and isinstance(result[1], Exception):
        raise result[1]
    return result[0]


def calcular_rota(moeda_base, m1, m2, ticker_dict, todos_pares, capital_inicial, aplicar_taxa_fn, buscar_preco_fn, exchange_obj):
    timestamp = str(datetime.now())
    rota_id = f"{moeda_base}_{m1}_{m2}_{moeda_base}"
    modo_execucao = "simulacao"
    exchange_nome = exchange_obj.get_nome()

    log.info("Iniciando cálculo da rota", categoria="calcular_rota", dados={"rota_id": rota_id, "exchange": exchange_nome})

    try:
        par1, tipo1, preco1, vol1, bruto1, m1_recebido = calcular_etapa(
            moeda_base, m1, capital_inicial, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn, exchange_obj
        )
        par2, tipo2, preco2, vol2, bruto2, m2_recebido = calcular_etapa(
            m1, m2, m1_recebido, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn, exchange_obj
        )
        par3, tipo3, preco3, vol3, bruto3, valor_final = calcular_etapa(
            m2, moeda_base, m2_recebido, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn, exchange_obj
        )

        lucro_real = valor_final - capital_inicial
        lucro_pct = (lucro_real / capital_inicial) * 100
        lucro_pct_sem_taxa = ((bruto3 - capital_inicial) / capital_inicial) * 100
        spread_total = abs(preco1 - preco2) + abs(preco2 - preco3)

        resultado = {
            "rota_id": rota_id,
            "rota": f"{moeda_base} → {m1} → {m2} → {moeda_base}",
            "par1": par1, "preco1": preco1, "tipo1": tipo1, "vol1": vol1, "m1_recebido": round(m1_recebido, 6),
            "par2": par2, "preco2": preco2, "tipo2": tipo2, "vol2": vol2, "m2_recebido": round(m2_recebido, 6),
            "par3": par3, "preco3": preco3, "tipo3": tipo3, "vol3": vol3,
            "valor_inicial": capital_inicial,
            "valor_final": round(valor_final, 6),
            "lucro_real": round(lucro_real, 6),
            "lucro_percentual": round(lucro_pct, 6),
            "lucro_sem_taxa": round(lucro_pct_sem_taxa, 6),
            "spread_total": round(spread_total, 6),
            "valores_brutos": {"etapa1": round(bruto1, 6), "etapa2": round(bruto2, 6), "etapa3": round(bruto3, 6)},
            "precos_brutos": {"par1": preco1, "par2": preco2, "par3": preco3},
            "exchange": exchange_nome,
            "modo_execucao": modo_execucao,
            "timestamp": timestamp,
            "status": "OK"
        }

        if lucro_pct > LUCRO_IRREALISTA:
            log.debug("Lucro irrealista detectado", categoria="lucro_irreal", dados=resultado, id=rota_id)
        if spread_total > 50:
            log.debug("Spread total excessivo", categoria="spread_excessivo", dados=resultado, id=rota_id)
        if any([preco1 is None, preco2 is None, preco3 is None, valor_final <= 0]):
            raise ValueError("🚨 Resultado inválido detectado.")

        log.debug("Cálculo de rota concluído", categoria="calcular_rota", dados=resultado, id=rota_id)
        return resultado

    except Exception as e:
        log.erro("Erro no cálculo da rota", categoria="rota_erro", dados={
            "rota_id": rota_id,
            "moeda_base": moeda_base,
            "m1": m1,
            "m2": m2,
            "erro": str(e),
            "timestamp": timestamp
        }, id=rota_id)
        return None


def construir_par(m1, m2, todos_pares):
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None


def inferir_tipo_operacao(par, moeda_origem):
    return "sell" if par.startswith(moeda_origem) else "buy"


def calcular_etapa(origem, destino, capital, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn, exchange_obj):
    inicio_etapa = time()
    par = construir_par(origem, destino, todos_pares)
    tipo = inferir_tipo_operacao(par, origem)

    log.debug("Iniciando etapa de cálculo", categoria="etapa_inicio", dados={
        "par": par,
        "tipo": tipo,
        "capital": capital,
        "origem": origem,
        "destino": destino
    })

    preco, volume = timeout_fn(buscar_preco_fn, 5, exchange_obj, par, tipo, capital)

    if not preco or not volume:
        log.debug("Liquidez insuficiente em etapa", categoria="etapa_liquidez", dados={
            "par": par,
            "origem": origem,
            "destino": destino,
            "capital": capital,
            "preco": preco,
            "volume": volume
        }, id=f"{origem}_{destino}")
        raise ValueError(f"[LIQUIDEZ] Preço ou volume ausente para {par}")

    bruto = capital * preco if tipo == "sell" else capital / preco
    recebido = aplicar_taxa_fn(bruto)
    duracao = round(time() - inicio_etapa, 3)

    log.debug("Etapa concluída", categoria="etapa_ok", dados={
        "par": par,
        "tipo": tipo,
        "preco": preco,
        "volume": volume,
        "bruto": bruto,
        "recebido": recebido,
        "origem": origem,
        "destino": destino,
        "duracao": f"{duracao}s"
    })

    return par, tipo, preco, volume, bruto, recebido
