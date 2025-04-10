import os
from dotenv import load_dotenv
load_dotenv()

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
