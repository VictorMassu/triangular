# main.py
import time
from datetime import datetime
from bot.estrategias.triangular.analisador import TriangularStrategy
from logs.logs_core.logger import log
from bot.config import MODO_LOOP, INTERVALO_LOOP
from bot.estrategias.triangular import simulador

def executar_analise():
    inicio = datetime.now()
    log.info("Iniciando execução da estratégia", categoria="main")

    try:
        estrategia = TriangularStrategy()
        estrategia.analisar()
    except Exception as e:
        log.erro("Erro inesperado na execução da estratégia", categoria="main", dados={"erro": str(e)})
    finally:
        fim = datetime.now()
        duracao = fim - inicio
        log.info(f"Execução finalizada em {duracao.total_seconds():.2f} segundos", categoria="main")

def main():
    try:
        if MODO_LOOP:
            log.info("🔁 MODO LOOP ATIVADO — O sistema ficará rodando continuamente.", categoria="main")
            while True:
                executar_analise()
                log.info(f"Aguardando {INTERVALO_LOOP} segundos para próxima varredura...", categoria="main")
                time.sleep(INTERVALO_LOOP)
        else:
            executar_analise()
    except KeyboardInterrupt:
        simulador.rodando = False  # <--- Sinaliza para as threads finalizarem
        log.info("🛑 Ctrl+C detectado — encerrando execução com segurança...", categoria="main")
        time.sleep(1)
        exit(0)

if __name__ == "__main__":
    main()
