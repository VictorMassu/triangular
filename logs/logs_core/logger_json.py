# logger_json.py
import json
import os
from threading import Lock
from bot_triangular.config import LOG_ROTAS

_lock = Lock()

def salvar_json_lista(caminho, nova_entrada):
    print(f"\n[DEBUG] 📝 Tentando salvar em: {os.path.abspath(caminho)}")
    print(f"[DEBUG] Tipo de entrada: {'lista' if isinstance(nova_entrada, list) else 'item único'}")

    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    with _lock:
        # 🔧 FORÇA CRIAÇÃO DO ARQUIVO SE NÃO EXISTIR
        if not os.path.exists(caminho):
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("[DEBUG] 📁 Arquivo criado vazio.")

        try:
            with open(caminho, "r", encoding="utf-8") as f:
                lista = json.load(f)
            print("[DEBUG] 📄 Log existente carregado.")
        except json.JSONDecodeError:
            print("[DEBUG] ⚠️ JSON corrompido ou vazio. Criando lista nova.")
            lista = []

        if isinstance(nova_entrada, list):
            lista.extend(nova_entrada)
        else:
            lista.append(nova_entrada)

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(lista, f, indent=4, ensure_ascii=False)
            print("[DEBUG] ✅ Log salvo com sucesso!")
        except Exception as e:
            print(f"[DEBUG] ❌ Erro ao salvar o arquivo: {e}")
