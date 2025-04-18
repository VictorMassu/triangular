from bot.estrategias.base_estrategias import BaseStrategy
from bot.estrategias.triangular.simulador import simular_rotas
from bot.estrategias.triangular.utils import get_exchange
from bot.config import USE_BINANCE, USE_BYBIT, VOLUME_MINIMO_PARA_ANALISE
from logs.logs_core.logger import log

class TriangularStrategy(BaseStrategy):
    def __init__(self):
        self.exchanges = []

        if USE_BINANCE:
            self.exchanges.append(get_exchange("BINANCE"))
            log.debug("Exchange Binance ativada", categoria="triangular")

        if USE_BYBIT:
            self.exchanges.append(get_exchange("BYBIT"))
            log.debug("Exchange Bybit ativada", categoria="triangular")

        if not self.exchanges:
            log.erro("Nenhuma exchange ativada no config", categoria="triangular")

    def analisar(self):
        log.info("Iniciando execução da estratégia Triangular", categoria="triangular")

        for ex in self.exchanges:
            nome = ex.get_nome()
            log.info(f"Analisando oportunidades na {nome}", categoria="triangular", dados={"exchange": nome})

            try:
                log.debug("Iniciando simulação paralela de rotas", categoria="simulador")
                simular_rotas(ex, volume_minimo=VOLUME_MINIMO_PARA_ANALISE)
            except KeyboardInterrupt:
                log.erro("Execução interrompida manualmente com Ctrl+C", categoria="parada")
                break
            except Exception as e:
                log.erro("Erro inesperado durante a simulação de rotas", categoria="erro_geral", dados={"erro": str(e), "exchange": nome})

        log.info("Execução da estratégia Triangular finalizada", categoria="triangular")

    def executar(self):
        log.info("Executar() ainda não implementado para a TriangularStrategy", categoria="triangular")
