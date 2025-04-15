import itertools
from bot_triangular.analisador.calcular_rota import calcular_rota
from logs.logs_agent.logger_console import log_info
from logs.logs_agent.logger_debug import log_debug_json
from bot_triangular.analisador.avaliador import aplicar_taxa, buscar_preco_ticker
from bot_triangular.config import (
    VALOR_INICIAL, MOEDA_BASE, LUCRO_MINIMO, LOG_ROTAS, LOG_OPORTUNIDADES,
    VOLUME_MINIMO_PARA_ANALISE, VALOR_MINIMO_MOEDA,
    TOP_MOEDAS
)
from logs.logs_core.logger_json import salvar_json_lista
from datetime import datetime


def simular_rotas(exchange, volume_minimo=VOLUME_MINIMO_PARA_ANALISE):
    pares = exchange.filtrar_pares_por_volume(volume_minimo)
    log_info(f"🔍 {len(pares)} pares com volume > {volume_minimo}")

    ticker_dict = {p['symbol']: p for p in pares}
    todos_pares = set(ticker_dict.keys())

    moedas_com_usdt = set()
    for par in todos_pares:
        if par.startswith(MOEDA_BASE):
            moedas_com_usdt.add(par[len(MOEDA_BASE):])
        elif par.endswith(MOEDA_BASE):
            moedas_com_usdt.add(par[:-len(MOEDA_BASE)])

    moedas_filtradas = sorted([m for m in moedas_com_usdt if not any(x in m for x in ['UP', 'DOWN'])])[:TOP_MOEDAS]

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

            print(f"\n[DEBUG] 🔄 Testando rota: {MOEDA_BASE} → {m1} → {m2} → {MOEDA_BASE}")
            print(f"[DEBUG] 🔗 Pares formados: {par1}, {par2}, {par3}")

            if not (par1 and par2 and par3):
                print(f"[DEBUG] ⚠️ Par(es) inválido(s), rota descartada.")
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

            print(f"[DEBUG] 📈 Resultado calculado com sucesso:\n{resultado}")

            if resultado:
                salvar_json_lista(LOG_ROTAS, resultado)
                print(f"[DEBUG] 💾 Resultado salvo no log de rotas!")

                if resultado["lucro_percentual"] >= LUCRO_MINIMO * 100:
                    print(f"[DEBUG] 🎯 Lucro acima do mínimo! Salvando como oportunidade...")
                    salvar_json_lista(LOG_OPORTUNIDADES, resultado)
            else:
                print(f"[DEBUG] ⚠️ Resultado nulo, será salvo no debug_log.json")
                log_debug_json(
                    mensagem=f"Resultado None ao simular rota {m1}-{m2}",
                    categoria="rota_nula",
                    dados={
                        "moeda_base": MOEDA_BASE,
                        "m1": m1,
                        "m2": m2,
                        "par1": par1,
                        "par2": par2,
                        "par3": par3,
                        "timestamp": datetime.now().isoformat()
                    }
                )

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
                }
            )


def construir_par(m1, m2, todos_pares):
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None
