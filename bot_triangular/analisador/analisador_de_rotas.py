# analisador_de_rotas.py

from bot_triangular.analisador.simulador import simular_rotas
from bot_triangular.analisador.utils import get_exchange
from logs.logs_agent.logger_console import log_info, log_erro
from bot_triangular.config import USE_BINANCE, USE_BYBIT, VOLUME_MINIMO_PARA_ANALISE

def analisar_oportunidades():
    log_info("🟢 Iniciando execução do analisador de oportunidades")

    exchanges = []
    if USE_BINANCE:
        exchanges.append(get_exchange("BINANCE"))
    if USE_BYBIT:
        exchanges.append(get_exchange("BYBIT"))

    if not exchanges:
        log_erro("❌ Nenhuma exchange ativada no config. Verifique USE_BINANCE / USE_BYBIT.")
        return

    for ex in exchanges:
        log_info(f"🚀 Iniciando análise: {ex.nome}")
        simular_rotas(ex, volume_minimo=VOLUME_MINIMO_PARA_ANALISE)

    log_info("✅ Execução finalizada")
