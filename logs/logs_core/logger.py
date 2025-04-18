import inspect
from datetime import datetime
from bot.config import DEBUG_LOG_PATH, LOG_ROTAS, LOG_OPORTUNIDADES
from logs.logs_core.logger_json import salvar_json_lista

class Logger:
    def __init__(self, print_terminal=True):
        self.print_terminal = print_terminal

    def _log(self, nivel, mensagem, categoria="geral", dados=None, id=None):
        origem = inspect.stack()[2].function  # quem chamou o logger
        timestamp = str(datetime.now())

        log_obj = {
            "timestamp": timestamp,
            "nivel": nivel.upper(),
            "categoria": categoria,
            "origem": origem,
            "mensagem": mensagem,
            "id": id,
            "dados": dados or {}
        }

        if self.print_terminal:
            print(f"[{nivel.upper()}] {timestamp} — [{categoria.upper()}] {mensagem} | origem: {origem}")

        salvar_json_lista(DEBUG_LOG_PATH, log_obj)

    def info(self, mensagem, categoria="geral", dados=None, id=None):
        self._log("INFO", mensagem, categoria, dados, id)

    def debug(self, mensagem, categoria="geral", dados=None, id=None):
        self._log("DEBUG", mensagem, categoria, dados, id)

    def erro(self, mensagem, categoria="geral", dados=None, id=None):
        self._log("ERRO", mensagem, categoria, dados, id)

    def salvar_debug(self, mensagem, categoria="debug", dados=None, id=None, silencioso=False):
        origem = inspect.stack()[1].function
        timestamp = str(datetime.now())

        entrada = {
            "timestamp": timestamp,
            "categoria": categoria,
            "origem": origem,
            "mensagem": mensagem,
            "id": id,
            "dados": dados or {}
        }

        if not silencioso and self.print_terminal:
            print(f"\n[🪵 DEBUG LOG] [{categoria.upper()}] {mensagem} — função: {origem}")

        salvar_json_lista(DEBUG_LOG_PATH, entrada)

    def salvar_rota(self, dados_rota):
        salvar_json_lista(LOG_ROTAS, dados_rota)

    def salvar_oportunidade(self, dados_oportunidade):
        salvar_json_lista(LOG_OPORTUNIDADES, dados_oportunidade)


# Instância global para uso direto
log = Logger()
