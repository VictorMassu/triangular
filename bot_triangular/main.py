from bot_triangular.analisador.analisador_de_rotas import analisar_oportunidades
from logs.logs_agent.logger_console import log_info
from datetime import datetime
from bot_triangular.config import MODO_LOOP, INTERVALO_LOOP
import time

def executar_analise():
    inicio = datetime.now()
    log_info("🟢 Iniciando execução do analisador de oportunidades")
    
    try:
        analisar_oportunidades()
    except Exception as e:
        log_info(f"❌ Erro inesperado na execução: {e}")
    finally:
        fim = datetime.now()
        duracao = fim - inicio
        log_info(f"✅ Execução finalizada em {duracao.total_seconds():.2f} segundos")

def main():
    if MODO_LOOP:
        log_info("🔁 MODO LOOP ATIVADO — O sistema ficará rodando continuamente.")
        while True:
            executar_analise()
            log_info(f"⏳ Aguardando {INTERVALO_LOOP} segundos para próxima varredura...\n")
            time.sleep(INTERVALO_LOOP)
    else:
        executar_analise()

if __name__ == "__main__":
    main()
