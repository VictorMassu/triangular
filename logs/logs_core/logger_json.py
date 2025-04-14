# logger_json.py
import json
import os

def salvar_json_lista(caminho, nova_entrada):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)  # ✅ Garante que a pasta existe

    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                lista = json.load(f)
        except json.JSONDecodeError:
            lista = []
    else:
        lista = []

    lista.append(nova_entrada)

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)
