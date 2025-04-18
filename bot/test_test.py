import os
from dotenv import load_dotenv

load_dotenv()
print("BASE_URL_BYBIT_PROD:", os.getenv("BASE_URL_BYBIT_PROD"))