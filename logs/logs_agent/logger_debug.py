# bot_triangular/logs/logs_agent/logger_debug.py

from logs.logs_core.logger_json import salvar_json_lista
from datetime import datetime
import os
import inspect

# Caminho padronizado para debug
from bot_triangular.config import DEBUG_LOG_PATH

def log_debug_json(mensagem, categoria="geral", dados=None, id=None, silencioso=False):
    """
    Registra um log técnico de depuração (debug) em formato JSON.

    Parâmetros:
    - mensagem (str): Mensagem principal descritiva do evento.
    - categoria (str): Categoria ou área do código (ex: 'simulador', 'executor', 'api').
    - dados (dict): Dados adicionais relevantes (valores de variáveis, objetos, etc).
    - id (str): Identificador opcional (como id da rota).
    - silencioso (bool): Se True, não imprime no terminal.
    """
    caller = inspect.stack()[1].function  # função que chamou o log
    entrada = {
        "timestamp": str(datetime.now()),
        "categoria": categoria,
        "origem": caller,
        "mensagem": mensagem,
        "id": id,
        "dados": dados or {}
    }

    if not silencioso:
        print(f"\n[🪵 DEBUG LOG] [{categoria.upper()}] {mensagem} — função: {caller}")

    salvar_json_lista(DEBUG_LOG_PATH, entrada)
