# analisador_de_rotas.py

from bot_triangular.analisador.simulador import simular_rotas
from bot_triangular.analisador.utils import get_exchange
from bot_triangular.utils.logs import log_info

def analisar_oportunidades():
    exchanges = [get_exchange("BINANCE"), get_exchange("BYBIT")]
    for ex in exchanges:
        log_info(f"🚀 Iniciando análise: {ex.nome}")
        simular_rotas(ex, volume_minimo=1000)
