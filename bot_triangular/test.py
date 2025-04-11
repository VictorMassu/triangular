import json
import os
from datetime import datetime

def salvar_log_rota(rota_info):
    arquivo_logs = "log_rotas.json"
    
    if os.path.exists(arquivo_logs):
        with open(arquivo_logs, "r") as f:
            rotas = json.load(f)
    else:
        rotas = []

    rotas.append(rota_info)

    with open(arquivo_logs, "w") as f:
        json.dump(rotas, f, indent=4)

# Simulando uma rota
rota_teste = {
    "exchange": "TesteExchange",
    "rota": "USDT → BTC → ETH → USDT",
    "timestamp": str(datetime.now()),
    "valor_inicial": 100,
    "moedas": [],
    "valor_final": 101.2,
    "lucro_percentual": 1.2,
    "lucro_real": 1.2,
    "spread_maximo_encontrado": 0.03,
    "tempo_execucao_ms": 200
}

salvar_log_rota(rota_teste)
print("Arquivo gerado!")
