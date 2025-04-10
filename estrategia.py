# triangular/estrategia.py
def rodar_estrategia(exchange):
    from .verificador import encontrar_oportunidades
    from .simulador import simular_rotas

    oportunidades = encontrar_oportunidades(exchange)
    for o in oportunidades:
        simular_rotas(exchange, o)
