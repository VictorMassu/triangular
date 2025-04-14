# logs/logs_agent/logger_console.py

from datetime import datetime

def log_info(msg):
    print(f"[INFO] {datetime.now()} — {msg}")

def log_erro(msg):
    print(f"[ERRO] {datetime.now()} — {msg}")

def log_debug(msg):
    print(f"[DEBUG] {datetime.now()} — {msg}")
