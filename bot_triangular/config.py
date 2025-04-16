# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Configurações gerais
MOEDA_BASE = "USDC"
VALOR_INICIAL = 500 #Unidade monetária (float)
TAXA = 0.00075 #Percentual decimal (0.S01 = 1%)
LUCRO_MINIMO = 0.003 #Percentual decimal (0.002 = 0.2%)
SPREAD_MAXIMO = 0.05 #Percentual decimal (0.05 = 5%)
LUCRO_IRREALISTA = 500  # alerta para lucro muito alto
MOEDAS_BLACKLIST = {"FDUSD"} # {"BRL", "ARS", "UAH", "TRY", "VAI", "EUR", "FDUSD"}
VALOR_MINIMO_MOEDA = 0.001  #Unidade monetária (ex: 0.01) isso evita moedas com valor muoto baixo
VOLUME_MINIMO_PARA_ANALISE = 1000  # volume em USDC ou equivalente
TOP_MOEDAS = 15000  # Número de moedas mais líquidas analisadas
MAX_WORKERS = 20  # Número de threads para paralelismo
MODO_LOOP = os.getenv("MODO_LOOP", "false").lower() == "true" # Modo de loop infinito no scanner
INTERVALO_LOOP = 10  # Tempo entre ciclos, em segundos
USAR_PROFUNDIDADE_BOOK = True  # ou False para usar o método atual

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
    API_KEY_BYBIT = os.getenv("API_KEY_BYBIT")
    SECRET_BYBIT = os.getenv("SECRET_BYBIT")
    BASE_URL_BYBIT = os.getenv("BASE_URL_BYBIT")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DATA_DIR = os.path.join(BASE_DIR, 'logs', 'logs_data')
LOG_ROTAS = os.path.join(LOGS_DATA_DIR, 'log_rotas.json')
LOG_OPORTUNIDADES = os.path.join(LOGS_DATA_DIR, 'oportunidades.json')
DEBUG_LOG_PATH = os.path.join(LOGS_DATA_DIR, 'debug_log.json')
