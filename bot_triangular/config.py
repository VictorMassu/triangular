# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações gerais
MOEDA_BASE = "USDT"
VALOR_INICIAL = 100
TAXA = 0.01
LUCRO_MINIMO = 0.0002
SPREAD_MAXIMO = 0.05
LUCRO_IRREALISTA = 500  # alerta para lucro muito alto
MOEDAS_BLACKLIST = {"BRL", "ARS", "UAH", "TRY", "VAI", "EUR"}
VALOR_MINIMO_MOEDA = 0.01  # Ignorar moedas muito baratas

blacklist_pares = set()

# Variáveis de ambiente
AMBIENTE = os.getenv("AMBIENTE", "test")
USE_BINANCE = os.getenv("USE_BINANCE", "true").lower() == "true"
USE_BYBIT = os.getenv("USE_BYBIT", "false").lower() == "true"

if AMBIENTE == "test":
    API_KEY_BINANCE = os.getenv("BINANCE_API_KEY_TEST")
    SECRET_BINANCE = os.getenv("BINANCE_SECRET_TEST")
    BASE_URL_BINANCE = "https://testnet.binance.vision/api"
    API_KEY_BYBIT = os.getenv("API_KEY_BYBIT")
    SECRET_BYBIT = os.getenv("SECRET_BYBIT")
    BASE_URL_BYBIT = os.getenv("BASE_URL_BYBIT")
else:
    API_KEY_BINANCE = os.getenv("BINANCE_API_KEY_PROD")
    SECRET_BINANCE = os.getenv("BINANCE_SECRET_PROD")
    BASE_URL_BINANCE = "https://api.binance.com/api"

# Diretório de logs
PASTA_LOGS = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(PASTA_LOGS, exist_ok=True)

LOG_ROTAS = os.path.join(PASTA_LOGS, "log_rotas.json")
LOG_OPORTUNIDADES = os.path.join(PASTA_LOGS, "oportunidades.json")
