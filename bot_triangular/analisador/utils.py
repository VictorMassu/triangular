# utils.py
from bot_triangular.exchanges.binance.cliente import BinanceExchange
from bot_triangular.exchanges.bybit.cliente import BybitExchange

def get_exchange(exchange_type="BINANCE"):
    if exchange_type == "BINANCE":
        ex = BinanceExchange()
        ex.nome = "Binance"
        return ex
    elif exchange_type == "BYBIT":
        ex = BybitExchange()
        ex.nome = "Bybit"
        return ex
