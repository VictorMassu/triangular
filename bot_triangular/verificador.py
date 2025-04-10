# triangular/verificador.py
from bot_triangular.utils import logs
from bot_triangular.config import API_KEY_BINANCE

def encontrar_oportunidades(exchange):
    return [{
        "base": "USDC",
        "rota": ["USDC", "ETH", "BTC", "USDC"]
    }]