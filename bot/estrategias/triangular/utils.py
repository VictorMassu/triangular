# utils.py
from bot.exchanges.binance.cliente import BinanceExchange
from bot.exchanges.bybit.cliente import BybitExchange

def get_exchange(exchange_type="BINANCE"):
    if exchange_type == "BINANCE":
        ex = BinanceExchange()
        ex.nome = "Binance"
        return ex
    elif exchange_type == "BYBIT":
        ex = BybitExchange()
        ex.nome = "Bybit"
        return ex
