from logs.logs_agent.logger_debug import log_debug_json
import os

print(f"Caminho absoluto esperado: {os.path.abspath('logs/logs_data/debug_log.json')}")

log_debug_json(
    mensagem="🚨 Teste manual de erro",
    categoria="teste_manual",
    dados={"detalhe": "isso é um teste"}
)
