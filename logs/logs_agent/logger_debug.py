# bot_triangular/logs/logs_agent/logger_debug.py

from logs.logs_core.logger_json import salvar_json_lista
from datetime import datetime
import os

# Caminho padronizado para debug
from bot_triangular.config import DEBUG_LOG_PATH

def log_debug_json(mensagem, categoria="geral", dados=None):
    """
    Registra um log técnico de depuração (debug) em formato JSON.

    Parâmetros:
    - mensagem (str): Mensagem principal descritiva do evento.
    - categoria (str): Categoria ou área do código (ex: 'simulador', 'executor', 'api').
    - dados (dict): Dados adicionais relevantes (valores de variáveis, objetos, etc).
    """
    entrada = {
        "timestamp": str(datetime.now()),
        "categoria": categoria,
        "mensagem": mensagem,
        "dados": dados or {}
    }
    salvar_json_lista(DEBUG_LOG_PATH, entrada)
