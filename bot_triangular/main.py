from bot_triangular.analisador.analisador_de_rotas import analisar_oportunidades
from logs.logs_agent.logger_console import log_info
from datetime import datetime

def main():
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

if __name__ == "__main__":
    main()
