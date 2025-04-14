from bot_triangular.exchanges.bybit.cliente import BybitExchange
from bot_triangular.utils.logs import log_info, log_erro
import json
import os
import time

BLACKLIST_FILE = "bot_triangular/analisador/blacklist_bybit.json"

def gerar_blacklist_bybit():
    try:
        bybit = BybitExchange()
        symbols = bybit.get_symbols()
        log_info(f"📈 Bybit | {len(symbols)} pares encontrados para análise.")
        pares_invalidos = []

        for i, symbol in enumerate(symbols):
            try:
                # LOG de progresso a cada 20 pares
                if i % 20 == 0:
                    print(f"🔄 Verificando par {i}/{len(symbols)}: {symbol}")

                orderbook = bybit.get_orderbook(symbol, timeout=5)
                bids = orderbook.get("b", [])
                asks = orderbook.get("a", [])

                if not bids or not asks:
                    pares_invalidos.append(symbol)
                    continue

                best_bid = float(bids[0][1])
                best_ask = float(asks[0][1])

                if best_bid <= 0 or best_ask <= 0:
                    pares_invalidos.append(symbol)

            except Exception as e:
                log_erro(f"⚠️ Erro ao processar {symbol}: {e}")
                pares_invalidos.append(symbol)
                time.sleep(0.5)
                continue

            time.sleep(0.15)  # Delay leve entre as chamadas para evitar rate limit

        # Salvar blacklist
        os.makedirs(os.path.dirname(BLACKLIST_FILE), exist_ok=True)
        with open(BLACKLIST_FILE, "w") as f:
            json.dump({"bybit": pares_invalidos}, f, indent=2)

        log_info(f"✅ Bybit | {len(pares_invalidos)} pares inválidos salvos na blacklist.")
    except Exception as e:
        log_erro(f"❌ Erro crítico ao gerar blacklist da Bybit: {e}")

if __name__ == "__main__":
    gerar_blacklist_bybit()
