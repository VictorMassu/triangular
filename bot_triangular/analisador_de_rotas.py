# bot_triangular/analisador_de_rotas.py

import time
import itertools
from datetime import datetime
from bot_triangular.exchanges.binance.cliente import BinanceExchange
from bot_triangular.exchanges.bybit.cliente import BybitExchange
from bot_triangular.utils.logs import log_info

# === CONFIGURAÇÕES ===
EXCHANGE_ATIVA = "BYBIT"  # Opções: "BINANCE" ou "BYBIT"
MOEDA_BASE = "USDT"
VALOR_INICIAL = 100
TAXA = 0.001
LUCRO_MINIMO = 0.0011  # 0.11%
SPREAD_MAXIMO = 0.04  # 4%

MOEDAS_FORTES = {
    "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "AVAX", "DOGE", "MATIC", "LTC",
    "DOT", "SHIB", "UNI", "LINK", "ATOM", "OP", "TON", "INJ", "ARB", "PEPE",
    "APT", "SUI", "NEAR", "ETC", "RUNE", "STX", "TRX", "CAKE", "TWT", "TIA",
    "GMX", "IMX", "GALA", "MASK", "CHZ", "SNX", "MKR", "RPL"
}

blacklist_pares = set()

# Seleciona exchange ativa
def get_exchange():
    return BinanceExchange() if EXCHANGE_ATIVA == "BINANCE" else BybitExchange()

def aplicar_taxa(valor):
    return valor * (1 - TAXA)

def buscar_preco_ticker(ticker_dict, symbol, tipo, capital=VALOR_INICIAL):
    dados = ticker_dict[symbol]
    ask = float(dados.get("ask", 0))
    askQty = float(dados.get("askQty", 0))
    bid = float(dados.get("bid", 0))
    bidQty = float(dados.get("bidQty", 0))

    spread = abs(ask - bid) / ((ask + bid) / 2)
    if spread > SPREAD_MAXIMO:
        raise ValueError(f"❌ Spread alto em {symbol}: {spread*100:.2f}%")

    if tipo == "buy":
        if askQty * ask < capital:
            raise ValueError(f"❌ Liquidez insuficiente para comprar {symbol}")
        return ask, askQty
    else:
        if bidQty < (capital / bid):
            raise ValueError(f"❌ Liquidez insuficiente para vender {symbol}")
        return bid, bidQty

def simular_rotas(exchange, volume_minimo=1000):
    pares_filtrados = exchange.filtrar_pares_por_volume(volume_minimo)
    log_info(f"🔍 {len(pares_filtrados)} pares filtrados com volume > {volume_minimo}")
    ticker_dict = {p['symbol']: p for p in pares_filtrados}
    todos_pares = set(ticker_dict.keys())
    moedas = {m for p in todos_pares for m in MOEDAS_FORTES if m in p}

    for m1, m2 in itertools.permutations(moedas, 2):
        par1 = par2 = par3 = None
        try:
            rota = f"{MOEDA_BASE} → {m1} → {m2} → {MOEDA_BASE}"
            log_info(f"Testando rota: {rota}")

            par1 = f"{m1}{MOEDA_BASE}" if f"{m1}{MOEDA_BASE}" in todos_pares else f"{MOEDA_BASE}{m1}"
            if par1 not in todos_pares or par1 in blacklist_pares:
                continue
            tipo1 = 'buy' if par1.startswith(MOEDA_BASE) else 'sell'
            preco1, vol1 = buscar_preco_ticker(ticker_dict, par1, tipo1)
            m1_recebido = aplicar_taxa(VALOR_INICIAL / preco1 if tipo1 == 'buy' else VALOR_INICIAL * preco1)

            par2 = f"{m1}{m2}" if f"{m1}{m2}" in todos_pares else f"{m2}{m1}"
            if par2 not in todos_pares or par2 in blacklist_pares:
                continue
            tipo2 = 'sell' if par2.startswith(m1) else 'buy'
            preco2, vol2 = buscar_preco_ticker(ticker_dict, par2, tipo2, capital=m1_recebido)
            m2_recebido = aplicar_taxa(m1_recebido * preco2 if tipo2 == 'sell' else m1_recebido / preco2)

            par3 = f"{m2}{MOEDA_BASE}" if f"{m2}{MOEDA_BASE}" in todos_pares else f"{MOEDA_BASE}{m2}"
            if par3 not in todos_pares or par3 in blacklist_pares:
                continue
            tipo3 = 'sell' if par3.startswith(m2) else 'buy'
            preco3, vol3 = buscar_preco_ticker(ticker_dict, par3, tipo3, capital=m2_recebido)
            usdc_final = aplicar_taxa(m2_recebido * preco3 if tipo3 == 'sell' else m2_recebido / preco3)

            lucro = usdc_final - VALOR_INICIAL
            lucro_pct = (lucro / VALOR_INICIAL) * 100

            if lucro_pct >= LUCRO_MINIMO * 100:
                print("\n✅ OPORTUNIDADE ENCONTRADA!")
                print(f"Rota: {rota}")
                print(f"Lucro: {lucro_pct:.4f}%  |  {MOEDA_BASE} final: {usdc_final:.4f}\n")
                print("Detalhes da operação:")
                print(f"1) {MOEDA_BASE} ➞ {m1} via {par1} | Tipo: {tipo1.upper()} | Preço: {preco1:.6f} | Vol: {vol1:.2f}")
                print(f"2) {m1} ➞ {m2} via {par2} | Tipo: {tipo2.upper()} | Preço: {preco2:.6f} | Vol: {vol2:.2f}")
                print(f"3) {m2} ➞ {MOEDA_BASE} via {par3} | Tipo: {tipo3.upper()} | Preço: {preco3:.6f} | Vol: {vol3:.2f}")

                return {
                    'rota': rota,
                    'usdc_final': round(usdc_final, 4),
                    'lucro_%': round(lucro_pct, 4)
                }

        except Exception as e:
            log_info(f"Erro ao testar rota {m1} → {m2}: {e}")
            for p in [par1, par2, par3]:
                if p: blacklist_pares.add(p)
            continue

    return None

def analisar_oportunidades():
    exchange = get_exchange()

    while True:
        log_info("🔄 Verificando oportunidades de arbitragem...")
        oportunidade = simular_rotas(exchange, volume_minimo=10000)

        if oportunidade:
            break
        else:
            print("⏳ Nenhuma oportunidade lucrativa. Repetindo em 5 segundos...\n")
            time.sleep(5)
