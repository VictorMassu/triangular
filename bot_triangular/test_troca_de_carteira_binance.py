import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

from bot_triangular.config import API_KEY_BINANCE, SECRET_BINANCE, BASE_URL_BINANCE, AMBIENTE

timestamp = int(time.time() * 1000)

params = {
    "type": "1",             # 1 = Funding -> Spot
    "asset": "USDC",
    "amount": "100",
    "timestamp": timestamp
}

query_string = urlencode(params)
signature = hmac.new(SECRET_BINANCE.encode(), query_string.encode(), hashlib.sha256).hexdigest()
params["signature"] = signature

headers = {
    "X-MBX-APIKEY": API_KEY_BINANCE
}

url = f"{BASE_URL_BINANCE}/sapi/v1/asset/transfer"
response = requests.post(url, headers=headers, params=params)

print(response.status_code)
print(response.json())
