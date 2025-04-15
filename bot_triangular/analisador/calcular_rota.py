from datetime import datetime
from logs.logs_core.logger_json import salvar_json_lista
from logs.logs_agent.logger_debug import log_debug_json
from bot_triangular.config import LOG_ROTAS, LOG_OPORTUNIDADES, LUCRO_IRREALISTA

def calcular_rota(moeda_base, m1, m2, ticker_dict, todos_pares, capital_inicial, aplicar_taxa_fn, buscar_preco_fn, exchange_nome="Binance"):
    try:
        def construir_par(m1, m2):
            if f"{m1}{m2}" in todos_pares:
                return f"{m1}{m2}"
            elif f"{m2}{m1}" in todos_pares:
                return f"{m2}{m1}"
            return None

        def inferir_tipo_operacao(par, moeda_origem):
            return "sell" if par.startswith(moeda_origem) else "buy"

        timestamp = str(datetime.now())
        rota_id = f"{moeda_base}_{m1}_{m2}_{moeda_base}"
        modo_execucao = "simulacao"

        print(f"\n[DEBUG] 🧠 Iniciando cálculo da rota: {moeda_base} → {m1} → {m2} → {moeda_base}")

        # Etapa 1
        par1 = construir_par(moeda_base, m1)
        tipo1 = inferir_tipo_operacao(par1, moeda_base)
        preco1, vol1 = buscar_preco_fn(ticker_dict, par1, tipo1, capital=capital_inicial)
        if not preco1 or not vol1:
            raise ValueError(f"[LIQUIDEZ] Preço ou volume ausente para {par1}")
        bruto1 = capital_inicial * preco1 if tipo1 == "sell" else capital_inicial / preco1
        m1_recebido = aplicar_taxa_fn(bruto1)

        # Etapa 2
        par2 = construir_par(m1, m2)
        tipo2 = inferir_tipo_operacao(par2, m1)
        preco2, vol2 = buscar_preco_fn(ticker_dict, par2, tipo2, capital=m1_recebido)
        if not preco2 or not vol2:
            raise ValueError(f"[LIQUIDEZ] Preço ou volume ausente para {par2}")
        bruto2 = m1_recebido * preco2 if tipo2 == "sell" else m1_recebido / preco2
        m2_recebido = aplicar_taxa_fn(bruto2)

        # Etapa 3
        par3 = construir_par(m2, moeda_base)
        tipo3 = inferir_tipo_operacao(par3, m2)
        preco3, vol3 = buscar_preco_fn(ticker_dict, par3, tipo3, capital=m2_recebido)
        if not preco3 or not vol3:
            raise ValueError(f"[LIQUIDEZ] Preço ou volume ausente para {par3}")
        bruto3 = m2_recebido * preco3 if tipo3 == "sell" else m2_recebido / preco3
        valor_final = aplicar_taxa_fn(bruto3)

        # Cálculo de lucro
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
