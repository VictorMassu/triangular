# config.py
import os
from dotenv import load_dotenv
load_dotenv()

AMBIENTE = os.getenv("AMBIENTE", "test")
API_KEY_BINANCE = os.getenv("API_KEY_BINANCE")
SECRET_BINANCE = os.getenv("SECRET_BINANCE")
