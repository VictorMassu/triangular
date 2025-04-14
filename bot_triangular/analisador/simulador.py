import itertools
from bot_triangular.analisador.calcular_rota import calcular_rota
from logs.logs_agent.logger_console import log_info
from logs.logs_agent.logger_debug import log_debug_json
from bot_triangular.analisador.avaliador import aplicar_taxa, buscar_preco_ticker
from bot_triangular.config import (
    VALOR_INICIAL, MOEDA_BASE, LUCRO_MINIMO,
    VOLUME_MINIMO_PARA_ANALISE, VALOR_MINIMO_MOEDA
)

from logs.logs_core.logger_json import salvar_json_lista


def simular_rotas(exchange, volume_minimo=VOLUME_MINIMO_PARA_ANALISE):
    pares = exchange.filtrar_pares_por_volume(volume_minimo)
    log_info(f"🔍 {len(pares)} pares com volume > {volume_minimo}")

    ticker_dict = {p['symbol']: p for p in pares}
    todos_pares = set(ticker_dict.keys())

    # 1. Coleta moedas com par com a moeda base
    moedas_com_usdt = set()
    for par in todos_pares:
        if par.startswith(MOEDA_BASE):
            moedas_com_usdt.add(par[len(MOEDA_BASE):])
        elif par.endswith(MOEDA_BASE):
            moedas_com_usdt.add(par[:-len(MOEDA_BASE)])

    log_info(f"🔎 {len(moedas_com_usdt)} moedas com pares {MOEDA_BASE} encontradas")

    # 2. Filtra combinações m1 → m2 onde o par realmente existe
    rotas_validas = []
    for m1 in moedas_com_usdt:
        for m2 in moedas_com_usdt:
            if m1 == m2:
                continue
            par2 = construir_par(m1, m2, todos_pares)
            if par2:  # só continua se par intermediário realmente existir
                rotas_validas.append((m1, m2))

    log_info(f"🔁 {len(rotas_validas)} rotas triangulares válidas encontradas")

    # 3. Processa apenas rotas válidas
    for m1, m2 in rotas_validas:
        try:
            par1 = construir_par(MOEDA_BASE, m1, todos_pares)
            par2 = construir_par(m1, m2, todos_pares)
            par3 = construir_par(m2, MOEDA_BASE, todos_pares)

            if not (par1 and par2 and par3):
                log_debug_json(
                    mensagem="Par(es) ausente(s) para rota triangular",
                    categoria="simulador",
                    dados={"m1": m1, "m2": m2, "par1": par1, "par2": par2, "par3": par3}
                )
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
                exchange_nome=exchange.nome
            )

            salvar_json_lista("bot_triangular/logs/arquivos/log_rotas.json", resultado)

            if resultado["lucro_percentual"] >= LUCRO_MINIMO * 100:
                salvar_json_lista("bot_triangular/logs/arquivos/oportunidades.json", resultado)

        except Exception as e:
            log_debug_json(
                mensagem="Erro na simulação de rota",
                categoria="simulador",
                dados={
                    "moeda_base": MOEDA_BASE,
                    "m1": m1,
                    "m2": m2,
                    "erro": str(e),
                    "par1": par1 if 'par1' in locals() else None,
                    "par2": par2 if 'par2' in locals() else None,
                    "par3": par3 if 'par3' in locals() else None
                }
            )


def construir_par(m1, m2, todos_pares):
    """
    Constrói o nome do par de acordo com a convenção da exchange.
    Ex: BTCUSDT ou USDTBTC
    """
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None
