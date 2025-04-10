# exchanges/binance/cliente.py
import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from exchanges.base_exchange import BaseExchange
from utils.logs import log_info, log_erro
from config import API_KEY_BINANCE, SECRET_BINANCE, AMBIENTE
from config import BASE_URL_BINANCE

class BinanceExchange(BaseExchange):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": API_KEY_BINANCE})

    def _signed_request(self, method, path, params=None):
        if params is None:
            params = {}
        params['timestamp'] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(SECRET_BINANCE.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        url = f"{BASE_URL_BINANCE}{path}?{query_string}&signature={signature}"

        try:
            response = self.session.request(method, url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"Erro na requisição assinada: {e}")
            return None

    def get_pares(self):
        url = f"{BASE_URL_BINANCE}/v3/exchangeInfo"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            pares = response.json()['symbols']
            return [p for p in pares if p['status'] == 'TRADING']
        except Exception as e:
            log_erro(f"Erro ao obter pares: {e}")
            return []

    def get_precos(self, par):
        url = f"{BASE_URL_BINANCE}/v3/ticker/bookTicker"
        try:
            response = self.session.get(url, params={"symbol": par})
            response.raise_for_status()
            data = response.json()
            return float(data['askPrice']), float(data['bidPrice'])
        except Exception as e:
            log_erro(f"Erro ao obter preços do par {par}: {e}")
            return None, None

    def executar_ordem(self, par, tipo, qtd, preco=None):
        path = "/v3/order"
        side = "BUY" if tipo.lower() == "compra" else "SELL"
        params = {
            "symbol": par,
            "side": side,
            "type": "MARKET",
            "quantity": qtd
        }
        if preco:
            params.update({"type": "LIMIT", "timeInForce": "GTC", "price": preco})

        return self._signed_request("POST", path, params)

    def consultar_saldo(self, moeda):
        path = "/v3/account"
        data = self._signed_request("GET", path)
        if not data:
            return 0.0
        for ativo in data.get("balances", []):
            if ativo['asset'] == moeda:
                return float(ativo['free'])
        return 0.0
