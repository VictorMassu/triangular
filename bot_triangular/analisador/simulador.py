import itertools
from bot_triangular.analisador.calcular_rota import calcular_rota
from bot_triangular.utils.logs import log_info


def simular_rotas(exchange, volume_minimo=1000):
    pares = exchange.filtrar_pares_por_volume(volume_minimo)
    log_info(f"🔍 {len(pares)} pares com volume > {volume_minimo}")
    ticker_dict = {p['symbol']: p for p in pares}
    todos_pares = set(ticker_dict.keys())

    # Identifica moedas únicas (exceto a moeda base)
    moedas_unicas = set()
    for par in todos_pares:
        for moeda in [par[:len(par)//2], par[len(par)//2:]]:
            if moeda != exchange.moeda_base:
                moedas_unicas.add(moeda)

    for m1, m2 in itertools.permutations(moedas_unicas, 2):
        calcular_rota(
            exchange=exchange,
            ticker_dict=ticker_dict,
            todos_pares=todos_pares,
            moeda_intermediaria1=m1,
            moeda_intermediaria2=m2
        )
