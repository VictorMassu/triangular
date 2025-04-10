# triangular/estrategia.py
from bot_triangular.verificador import encontrar_oportunidades
from bot_triangular.simulador import simular_rotas

def rodar_estrategia(exchange):

    oportunidades = encontrar_oportunidades(exchange)
    for o in oportunidades:
        simular_rotas(exchange, o)
