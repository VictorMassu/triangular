# bot_triangular/analisador_de_rotas.py
from itertools import permutations
from bot_triangular.utils.logs import log_info

MOEDA_BASE = "USDC"
VALOR_INICIAL = 100  # valor simulado por operação


def gerar_rotas_triangulares(pares_disponiveis):
    moedas = set()
    for par in pares_disponiveis:
        moedas.add(par['baseAsset'])
        moedas.add(par['quoteAsset'])

    rotas = []
    for combinacao in permutations(moedas, 3):
        if combinacao[0] == MOEDA_BASE and combinacao[2] == MOEDA_BASE:
            rota = list(combinacao) + [MOEDA_BASE]
            rotas.append(rota)
    return rotas


def validar_rotas_existentes(exchange, rotas):
    pares_validos = exchange.get_pares()
    nomes_pares = {par['symbol'] for par in pares_validos}
    rotas_validas = []

    for rota in rotas:
        par1 = rota[0] + rota[1]
        par2 = rota[1] + rota[2]
        par3 = rota[2] + rota[3]

        invertido1 = rota[1] + rota[0]
        invertido2 = rota[2] + rota[1]
        invertido3 = rota[3] + rota[2]

        if (par1 in nomes_pares or invertido1 in nomes_pares) and \
           (par2 in nomes_pares or invertido2 in nomes_pares) and \
           (par3 in nomes_pares or invertido3 in nomes_pares):
            rotas_validas.append(rota)

    return rotas_validas


def analisar_oportunidades(exchange):
    saldo = exchange.consultar_saldo(MOEDA_BASE)
    if saldo < VALOR_INICIAL:
        log_info(f"⚠️ Saldo insuficiente em {MOEDA_BASE}: {saldo}")
        return

    log_info("🔎 Gerando combinações de rotas triangulares...")
    pares_disponiveis = exchange.get_pares()
    rotas = gerar_rotas_triangulares(pares_disponiveis)
    rotas_validas = validar_rotas_existentes(exchange, rotas)

    log_info(f"🔁 {len(rotas_validas)} rotas triangulares válidas encontradas.")
    for rota in rotas_validas:
        oportunidade = {
            "base": MOEDA_BASE,
            "rota": rota
        }
        from bot_triangular.simulador import simular_rotas
        simular_rotas(exchange, oportunidade)
