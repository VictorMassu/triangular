import os
from dotenv import load_dotenv
load_dotenv()

AMBIENTE = os.getenv("AMBIENTE", "test")

if AMBIENTE == "test":
    API_KEY_BINANCE = os.getenv("BINANCE_API_KEY_TEST")
    SECRET_BINANCE = os.getenv("BINANCE_SECRET_TEST")
    BASE_URL_BINANCE = "https://testnet.binance.vision/api"
else:
    API_KEY_BINANCE = os.getenv("BINANCE_API_KEY_PROD")
    SECRET_BINANCE = os.getenv("BINANCE_SECRET_PROD")
    BASE_URL_BINANCE = "https://api.binance.com/api"
