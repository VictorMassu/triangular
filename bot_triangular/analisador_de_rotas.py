import json
import os
from bot_triangular.utils.logs import log_info
from itertools import permutations

MOEDA_BASE = "USDC"
VALOR_INICIAL = 100  # valor inicial por operação
LUCRO_MINIMO = 0.1 / 100  # lucro mínimo desejado (0.1%)

# Caminho do arquivo de banco de dados
PARES_DB_PATH = 'pares_validos.json'

def carregar_pares_db():
    """
    Carrega os pares válidos e não válidos do arquivo JSON.
    """
    if os.path.exists(PARES_DB_PATH):
        with open(PARES_DB_PATH, 'r') as file:
            db = json.load(file)
            # Garantindo que pares_validos e pares_invalidos sejam sets
            return {'validos': set(db.get('validos', [])), 'invalidos': set(db.get('invalidos', []))}
    return {'validos': set(), 'invalidos': set()}

def salvar_pares_db(pares_validos, pares_invalidos):
    """
    Salva os pares válidos e não válidos no arquivo JSON.
    """
    with open(PARES_DB_PATH, 'w') as file:
        json.dump({'validos': list(pares_validos), 'invalidos': list(pares_invalidos)}, file, indent=4)
    log_info(f"🔎 Banco de dados de pares atualizado: {len(pares_validos)} pares válidos, {len(pares_invalidos)} pares inválidos.")

def validar_par_cache(par, pares_validos, pares_invalidos):
    """
    Verifica se o par já foi validado previamente.
    """
    if par in pares_validos:
        return True
    if par in pares_invalidos:
        return False
    return None  # Significa que o par precisa ser validado

def gerar_rotas_triangulares(pares_disponiveis):
    moedas = set()
    for par in pares_disponiveis:
        moedas.add(par['baseAsset'])
        moedas.add(par['quoteAsset'])

    rotas = []
    # Gerando permutações de 3 moedas, onde USDC pode ser qualquer uma das 3
    for combinacao in permutations(moedas, 3):
        if MOEDA_BASE in combinacao:
            rota = list(combinacao)  # A rota pode ter qualquer moeda como final
            rotas.append(rota)

    return rotas

def validar_rotas_existentes(exchange, rotas, pares_validos, pares_invalidos):
    """
    Verifica se os pares das rotas são válidos com base no banco de dados.
    """
    nomes_pares = {par['symbol'] for par in exchange.get_pares()}
    rotas_validas = []

    for rota in rotas:
        par1 = rota[0] + rota[1]
        par2 = rota[1] + rota[2]

        # Invertidos para verificar os pares na ordem inversa
        invertido1 = rota[1] + rota[0]
        invertido2 = rota[2] + rota[1]

        # Verifica se o par existe no banco de dados ou se já foi validado
        if validar_par_cache(par1, pares_validos, pares_invalidos) and \
           validar_par_cache(par2, pares_validos, pares_invalidos):
            rotas_validas.append(rota)
        else:
            # Marca como inválido caso o par não seja encontrado
            if par1 not in pares_validos and par1 not in pares_invalidos:
                pares_invalidos.add(par1)
            if par2 not in pares_validos and par2 not in pares_invalidos:
                pares_invalidos.add(par2)

    log_info(f"🔎 Total de rotas triangulares válidas: {len(rotas_validas)}")
    return rotas_validas

def simular_oportunidade(exchange, rota):
    valor_atual = VALOR_INICIAL
    log_info(f"🔄 Iniciando simulação da oportunidade: {rota}")

    for i in range(len(rota) - 1):
        par = rota[i] + rota[i + 1]
        saldo = valor_atual

        # Obter o preço de compra e venda
        preco_compra, preco_venda = exchange.get_precos(par)
        if preco_compra is None or preco_venda is None:
            log_info(f"❌ Não foi possível obter preços para {par}. Pulando esta rota.")
            return 0

        # Realizar a troca de moeda
        quantidade = saldo / preco_compra
        valor_atual = quantidade * preco_venda

        log_info(f"💱 {rota[i]} → {rota[i + 1]} via {par} @ {preco_compra}/{preco_venda} → Novo saldo: {valor_atual} USDC")

    return valor_atual

def analisar_oportunidades(exchange):
    saldo = exchange.consultar_saldo(MOEDA_BASE)
    if saldo < VALOR_INICIAL:
        log_info(f"⚠️ Saldo insuficiente em {MOEDA_BASE}: {saldo}")
        return

    log_info("🔎 Carregando banco de dados de pares...")
    pares_validos, pares_invalidos = carregar_pares_db()

    log_info("🔎 Gerando combinações de rotas triangulares...")
    pares_disponiveis = exchange.get_pares()
    rotas = gerar_rotas_triangulares(pares_disponiveis)
    rotas_validas = validar_rotas_existentes(exchange, rotas, pares_validos, pares_invalidos)

    log_info(f"🔁 {len(rotas_validas)} rotas triangulares válidas encontradas.")
    for rota in rotas_validas:
        valor_final = simular_oportunidade(exchange, rota)
        lucro_percentual = (valor_final - VALOR_INICIAL) / VALOR_INICIAL * 100

        # Verificar se o lucro está acima do mínimo
        if lucro_percentual >= (LUCRO_MINIMO * 100):
            log_info(f"✅ Lucro de {lucro_percentual:.4f}% acima do mínimo ({LUCRO_MINIMO * 100}%) — EXECUTANDO 💥")
            # Aqui você pode adicionar a lógica para executar a operação real (compra e venda)
        else:
            log_info(f"⚠️ Lucro de {lucro_percentual:.4f}% abaixo do mínimo ({LUCRO_MINIMO * 100}%) — ignorado.")
    
    # Salva os pares válidos e inválidos no banco de dados
    salvar_pares_db(pares_validos, pares_invalidos)
