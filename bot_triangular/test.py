import requests
import itertools
import time

# ==========================
# CONFIGURAÇÕES DO SISTEMA
# ==========================

VALOR_INICIAL = 100        # Capital inicial em USDC
TAXA_TRADE = 0.001         # Taxa de trade padrão: 0.1%
LUCRO_MINIMO = 0.004       # Lucro mínimo desejado: 0.4%
BOOK_CACHE = {}            # Cache dos order books
MOEDA_BASE = 'USDC'        # Moeda inicial e final do ciclo
LOG_ERROS = True           # Salva os erros em arquivo
MOEDAS_FORTES = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "AVAX", "DOGE", "MATIC", "LTC"}

# ==========================
# FUNÇÕES DE UTILIDADE
# ==========================

def obter_pares_binance():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url).json()
    pares = [s['symbol'] for s in response['symbols'] if s['status'] == 'TRADING']
    return pares

def obter_book(symbol):
    if symbol in BOOK_CACHE:
        return BOOK_CACHE[symbol]
    url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=5"
    response = requests.get(url).json()

    bids = response.get('bids', [])
    asks = response.get('asks', [])
    BOOK_CACHE[symbol] = (bids, asks)
    time.sleep(0.05)  # prevenir rate limit
    return bids, asks

def buscar_preco_mercado(symbol, tipo):
    bids, asks = obter_book(symbol)

    if not bids or not asks:
        raise ValueError(f"Livro de ordens vazio para o par: {symbol}")

    if tipo == 'buy':
        return float(asks[0][0]), float(asks[0][1])  # Preço, Quantidade
    elif tipo == 'sell':
        return float(bids[0][0]), float(bids[0][1])
    return None, None

def aplicar_taxa(valor):
    return valor * (1 - TAXA_TRADE)

# ==========================
# SIMULAÇÃO DE TRIÂNGULO
# ==========================

def simular_triangulo(pares, moeda_base=MOEDA_BASE):
    resultados = []
    moedas_intermediarias = set(MOEDAS_FORTES)

    for par in pares:
        if par.startswith(moeda_base):
            moedas_intermediarias.add(par.replace(moeda_base, ''))
        elif par.endswith(moeda_base):
            moedas_intermediarias.add(par.replace(moeda_base, ''))

    for m1, m2 in itertools.permutations(moedas_intermediarias, 2):
        try:
            print(f"Testando rota: {moeda_base} → {m1} → {m2} → {moeda_base}")

            # ==================
            # Etapa 1: USDC → m1
            # ==================
            par1 = f"{m1}{moeda_base}" if f"{m1}{moeda_base}" in pares else f"{moeda_base}{m1}"
            if par1 not in pares:
                continue
            tipo1 = 'buy' if par1.startswith(moeda_base) else 'sell'
            preco1, liquidez1 = buscar_preco_mercado(par1, tipo1)
            if VALOR_INICIAL > preco1 * liquidez1:
                continue
            m1_recebido = aplicar_taxa(VALOR_INICIAL / preco1 if tipo1 == 'buy' else VALOR_INICIAL * preco1)

            # ==================
            # Etapa 2: m1 → m2
            # ==================
            par2 = f"{m1}{m2}" if f"{m1}{m2}" in pares else f"{m2}{m1}"
            if par2 not in pares:
                continue
            tipo2 = 'sell' if par2.startswith(m1) else 'buy'
            preco2, liquidez2 = buscar_preco_mercado(par2, tipo2)
            if m1_recebido > preco2 * liquidez2:
                continue
            m2_recebido = aplicar_taxa(m1_recebido * preco2 if tipo2 == 'sell' else m1_recebido / preco2)

            # ==================
            # Etapa 3: m2 → USDC
            # ==================
            par3 = f"{m2}{moeda_base}" if f"{m2}{moeda_base}" in pares else f"{moeda_base}{m2}"
            if par3 not in pares:
                continue
            tipo3 = 'sell' if par3.startswith(m2) else 'buy'
            preco3, liquidez3 = buscar_preco_mercado(par3, tipo3)
            if m2_recebido > preco3 * liquidez3:
                continue
            usdc_final = aplicar_taxa(m2_recebido * preco3 if tipo3 == 'sell' else m2_recebido / preco3)

            # ==================
            # Avaliação do lucro
            # ==================
            lucro = usdc_final - VALOR_INICIAL
            lucro_pct = (lucro / VALOR_INICIAL) * 100

            if lucro_pct >= LUCRO_MINIMO * 100:
                resultados.append({
                    'rota': f"{moeda_base} → {m1} → {m2} → {moeda_base}",
                    'usdc_final': round(usdc_final, 4),
                    'lucro_%': round(lucro_pct, 4)
                })
        except Exception as e:
            msg_erro = f"[Erro na rota {moeda_base} → {m1} → {m2} → {moeda_base}]: {e}"
            print(msg_erro)
            if LOG_ERROS:
                with open("rotas_invalidas.log", "a") as log:
                    log.write(msg_erro + "\n")
            continue

    return resultados

# ==========================
# EXECUÇÃO PRINCIPAL
# ==========================

if __name__ == "__main__":
    print("🔍 Buscando pares válidos da Binance...")
    pares_validos = obter_pares_binance()
    print(f"✅ {len(pares_validos)} pares encontrados.\n")

    print("🚀 Iniciando análise de arbitragem triangular...\n")
    oportunidades = simular_triangulo(pares_validos)

    if oportunidades:
        print("\n⚡ Oportunidades encontradas:")
        for op in sorted(oportunidades, key=lambda x: -x['lucro_%']):
            print(op)
    else:
        print("❌ Nenhuma oportunidade lucrativa encontrada.")
