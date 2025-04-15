from datetime import datetime
from logs.logs_core.logger_json import salvar_json_lista
from logs.logs_agent.logger_debug import log_debug_json
from bot_triangular.config import LOG_ROTAS, LOG_OPORTUNIDADES, LUCRO_IRREALISTA


def calcular_rota(moeda_base, m1, m2, ticker_dict, todos_pares, capital_inicial, aplicar_taxa_fn, buscar_preco_fn, exchange_nome="Binance"):
    try:
        timestamp = str(datetime.now())
        rota_id = f"{moeda_base}_{m1}_{m2}_{moeda_base}"
        modo_execucao = "simulacao"

        print(f"\n[DEBUG] 🧠 Iniciando cálculo da rota: {moeda_base} → {m1} → {m2} → {moeda_base}")

        # Etapas do ciclo
        par1, tipo1, preco1, vol1, bruto1, m1_recebido = calcular_etapa(
            moeda_base, m1, capital_inicial, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn
        )
        par2, tipo2, preco2, vol2, bruto2, m2_recebido = calcular_etapa(
            m1, m2, m1_recebido, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn
        )
        par3, tipo3, preco3, vol3, bruto3, valor_final = calcular_etapa(
            m2, moeda_base, m2_recebido, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn
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
            "valores_brutos": {
                "etapa1": round(bruto1, 6),
                "etapa2": round(bruto2, 6),
                "etapa3": round(bruto3, 6)
            },
            "precos_brutos": {
                "par1": preco1,
                "par2": preco2,
                "par3": preco3
            },
            "exchange": exchange_nome,
            "modo_execucao": modo_execucao,
            "timestamp": timestamp,
            "status": "OK"
        }

        if any([
            resultado["preco1"] is None,
            resultado["preco2"] is None,
            resultado["preco3"] is None,
            resultado["valor_final"] <= 0,
        ]):
            raise ValueError("🚨 Resultado inválido detectado.")

        return resultado

    except Exception as e:
        print(f"[DEBUG] ❌ Erro inesperado durante cálculo da rota: {e}")
        log_debug_json(
            mensagem=str(e),
            categoria="calcular_rota",
            dados={
                "moeda_base": moeda_base,
                "m1": m1,
                "m2": m2,
                "erro": str(e),
                "timestamp": str(datetime.now())
            }
        )
        return None


def construir_par(m1, m2, todos_pares):
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None


def inferir_tipo_operacao(par, moeda_origem):
    return "sell" if par.startswith(moeda_origem) else "buy"


def calcular_etapa(origem, destino, capital, ticker_dict, todos_pares, aplicar_taxa_fn, buscar_preco_fn):
    par = construir_par(origem, destino, todos_pares)
    tipo = inferir_tipo_operacao(par, origem)
    preco, volume = buscar_preco_fn(ticker_dict, par, tipo, capital=capital)
    if not preco or not volume:
        raise ValueError(f"[LIQUIDEZ] Preço ou volume ausente para {par}")

    bruto = capital * preco if tipo == "sell" else capital / preco
    recebido = aplicar_taxa_fn(bruto)
    return par, tipo, preco, volume, bruto, recebido
