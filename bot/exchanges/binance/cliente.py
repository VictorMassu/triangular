import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from bot.exchanges.base_exchange import BaseExchange
from logs.logs_agent.logger_console import log_info, log_erro
from bot.config import API_KEY_BINANCE, SECRET_BINANCE, BASE_URL_BINANCE


class BinanceExchange(BaseExchange):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": API_KEY_BINANCE})
        self.base_url = BASE_URL_BINANCE
        self.nome = "Binance"

    def get_nome(self) -> str:
        return self.nome

    def _get_server_time(self):
        url = f"{self.base_url}/v3/time"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()["serverTime"]
        except Exception as e:
            log_erro(f"[{self.nome}][_get_server_time] Erro: {e}")
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
            log_erro(f"[{self.nome}][_signed_request] Erro: {e}")
            return None

    def get_pares(self) -> list:
        try:
            response = self.session.get(f"{self.base_url}/v3/exchangeInfo")
            response.raise_for_status()
            data = response.json().get("symbols", [])
            pares = [s["symbol"] for s in data if s["status"] == "TRADING"]
            log_info(f"[{self.nome}][get_pares] {len(pares)} pares encontrados.")
            return pares
        except Exception as e:
            log_erro(f"[{self.nome}][get_pares] Erro: {e}")
            return []

    def get_precos(self, par: str) -> tuple:
        url = f"{self.base_url}/v3/ticker/bookTicker"
        try:
            response = self.session.get(url, params={"symbol": par})
            response.raise_for_status()
            data = response.json()
            ask = float(data["askPrice"])
            bid = float(data["bidPrice"])
            return ask, bid
        except Exception as e:
            log_erro(f"[{self.nome}][get_precos] Erro no par {par}: {e}")
            return None, None

    def consultar_saldo(self, moeda: str) -> float:
        path = "/v3/account"
        data = self._signed_request("GET", path)
        if not data:
            return 0.0

        moeda_normalizada = moeda.replace("-", "").replace("_", "").strip().upper()

        for ativo in data.get("balances", []):
            nome_ativo = ativo['asset'].replace("-", "").replace("_", "").strip().upper()
            if nome_ativo == moeda_normalizada:
                saldo = float(ativo['free'])
                log_info(f"[{self.nome}][consultar_saldo] Saldo {moeda}: {saldo}")
                return saldo

        log_info(f"[{self.nome}][consultar_saldo] Moeda {moeda} não encontrada.")
        return 0.0

    def executar_ordem(self, par: str, tipo: str, qtd: float, preco: float = None) -> dict:
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

    def get_book_tickers_completo(self):
        url = f"{self.base_url}/v3/ticker/bookTicker"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"[{self.nome}][get_book_tickers_completo] Erro: {e}")
            return []

    def get_volumes_24h(self):
        url = f"{self.base_url}/v3/ticker/24hr"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"[{self.nome}][get_volumes_24h] Erro: {e}")
            return []

    def get_market_data(self):
        books = self.get_book_tickers_completo()
        volumes = self.get_volumes_24h()
        volumes_dict = {v["symbol"]: float(v.get("quoteVolume", 0)) for v in volumes}
        return books, volumes_dict

    def filtrar_pares_por_volume(self, volume_minimo: float) -> list:
        symbols_validos = set(self.get_pares())
        books, volumes_dict = self.get_market_data()
        pares_filtrados = []

        for item in books:
            symbol = item["symbol"]

            if symbol not in symbols_validos:
                continue

            try:
                bid = float(item["bidPrice"])
                ask = float(item["askPrice"])
                volume = volumes_dict.get(symbol, 0.0)
            except (ValueError, KeyError):
                continue

            if volume >= volume_minimo:
                pares_filtrados.append({
                    "symbol": symbol,
                    "bid": bid,
                    "ask": ask
                })

        log_info(f"[{self.nome}][filtrar_pares_por_volume] {len(pares_filtrados)} pares válidos.")
        return pares_filtrados
