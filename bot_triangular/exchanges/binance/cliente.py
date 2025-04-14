# exchanges/binance/cliente.py

import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from bot_triangular.exchanges.base_exchange import BaseExchange
from logs.logs_agent.logger_console import log_info, log_erro
from bot_triangular.config import API_KEY_BINANCE, SECRET_BINANCE, BASE_URL_BINANCE


class BinanceExchange(BaseExchange):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": API_KEY_BINANCE})
        self.base_url = BASE_URL_BINANCE

    def _get_server_time(self):
        url = f"{self.base_url}/v3/time"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()["serverTime"]
        except Exception as e:
            log_erro(f"⏱️ Erro ao obter timestamp da Binance: {e}")
            return int(time.time() * 1000)

    def _signed_request(self, method, path, params=None):
        if params is None:
            params = {}

        params['timestamp'] = self._get_server_time()
        query_string = urlencode(params)
        signature = hmac.new(
            SECRET_BINANCE.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        url = f"{self.base_url}{path}?{query_string}&signature={signature}"

        try:
            response = self.session.request(method, url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"❌ Erro na requisição assinada (Binance): {e}")
            return None

    def get_symbols(self):
        try:
            response = self.session.get(f"{self.base_url}/v3/exchangeInfo")
            response.raise_for_status()
            return [s["symbol"] for s in response.json().get("symbols", []) if s["status"] == "TRADING"]
        except Exception as e:
            log_erro(f"❌ Erro ao obter symbols da Binance: {e}")
            return []

    def get_pares(self):
        return self.get_symbols()

    def get_precos(self, par):
        url = f"{self.base_url}/v3/ticker/bookTicker"
        try:
            response = self.session.get(url, params={"symbol": par})
            response.raise_for_status()
            data = response.json()
            return float(data['askPrice']), float(data['bidPrice'])
        except Exception as e:
            log_erro(f"❌ Erro ao obter preços do par {par} na Binance: {e}")
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
            log_erro("❌ Erro ao obter os dados da conta Binance.")
            return 0.0

        moeda_normalizada = moeda.replace("-", "").replace("_", "").strip().upper()

        for ativo in data.get("balances", []):
            nome_ativo = ativo['asset'].replace("-", "").replace("_", "").strip().upper()
            if nome_ativo == moeda_normalizada:
                saldo = float(ativo['free'])
                log_info(f"💰 Binance | Saldo disponível em {moeda}: {saldo}")
                return saldo

        log_info(f"⚠️ Binance | Moeda {moeda} não encontrada (após normalização).")
        return 0.0

    def converter_para_stable(self, moeda, stable="USDC"):
        par = moeda + stable
        saldo = self.consultar_saldo(moeda)

        if saldo <= 0:
            log_info(f"❌ Binance | Saldo insuficiente em {moeda} para conversão.")
            return

        log_info(f"🔁 Binance | Iniciando conversão de {saldo} {moeda} para {stable} via {par}")

        params = {
            "symbol": par,
            "side": "SELL",
            "type": "MARKET",
            "quantity": saldo
        }

        resultado = self._signed_request("POST", "/v3/order", params)

        if resultado:
            log_info(f"✅ Binance | Conversão executada com sucesso!")
        else:
            log_erro(f"❌ Binance | Erro ao tentar converter {moeda} para {stable}.")

    def get_book_tickers_completo(self):
        url = f"{self.base_url}/v3/ticker/bookTicker"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"❌ Binance | Erro ao obter todos os book tickers: {e}")
            return []

    def get_volumes_24h(self):
        url = f"{self.base_url}/v3/ticker/24hr"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"❌ Binance | Erro ao obter volumes de 24h: {e}")
            return []

    def get_market_data(self):
        books = self.get_book_tickers_completo()
        volumes = self.get_volumes_24h()
        volumes_dict = {v["symbol"]: float(v.get("quoteVolume", 0)) for v in volumes}
        return books, volumes_dict

    def filtrar_pares_por_volume(self, volume_minimo=100000):
        books, volumes_dict = self.get_market_data()
        pares_filtrados = []

        for item in books:
            symbol = item["symbol"]
            bid = float(item["bidPrice"])
            ask = float(item["askPrice"])
            volume = volumes_dict.get(symbol, 0.0)

            if volume >= volume_minimo:
                pares_filtrados.append({
                    "symbol": symbol,
                    "bid": bid,
                    "ask": ask,
                    "volume": volume
                })

        log_info(f"🔍 Binance | {len(pares_filtrados)} pares filtrados com volume > {volume_minimo}")
        return pares_filtrados
