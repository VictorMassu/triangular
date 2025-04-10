import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from bot_triangular.exchanges.base_exchange import BaseExchange
from bot_triangular.utils.logs import log_info, log_erro
from bot_triangular.config import API_KEY_BYBIT, SECRET_BYBIT, BASE_URL_BYBIT

class BybitExchange(BaseExchange):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-BYBIT-API-KEY": API_KEY_BYBIT})
        self.base_url = BASE_URL_BYBIT

    def _get_server_time(self):
        return int(time.time() * 1000)

    def _signed_request(self, method, path, params=None):
        if params is None:
            params = {}

        params["api_key"] = API_KEY_BYBIT
        params["timestamp"] = self._get_server_time()

        sorted_params = dict(sorted(params.items()))
        query_string = urlencode(sorted_params)
        signature = hmac.new(SECRET_BYBIT.encode(), query_string.encode(), hashlib.sha256).hexdigest()

        sorted_params["sign"] = signature
        url = f"{self.base_url}{path}?{urlencode(sorted_params)}"

        try:
            response = self.session.request(method, url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_erro(f"Erro na requisição Bybit: {e}")
            return None

    def get_pares(self):
        url = f"{self.base_url}/v5/market/instruments-info"
        try:
            response = self.session.get(url, params={"category": "spot"})
            response.raise_for_status()
            pares = response.json().get("result", {}).get("list", [])
            return [p for p in pares if p["status"] == "Trading"]
        except Exception as e:
            log_erro(f"Erro ao obter pares Bybit: {e}")
            return []

    def get_precos(self, par):
        url = f"{self.base_url}/v5/market/tickers"
        try:
            response = self.session.get(url, params={"category": "spot"})
            response.raise_for_status()
            tickers = response.json()["result"]["list"]
            for t in tickers:
                if t["symbol"] == par:
                    return float(t["askPrice"]), float(t["bidPrice"])
            return None, None
        except Exception as e:
            log_erro(f"Erro ao obter preços do par {par} na Bybit: {e}")
            return None, None

    def consultar_saldo(self, moeda):
        path = "/v5/account/wallet-balance"
        data = self._signed_request("GET", path, {"accountType": "UNIFIED"})
        if not data:
            return 0.0

        balances = data.get("result", {}).get("list", [])[0].get("coin", [])
        for b in balances:
            if b["coin"].upper() == moeda.upper():
                return float(b["availableToWithdraw"])
        return 0.0

    def executar_ordem(self, par, tipo, qtd, preco=None):
        side = "Buy" if tipo.lower() == "compra" else "Sell"
        params = {
            "category": "spot",
            "symbol": par,
            "side": side,
            "orderType": "Market",
            "qty": str(qtd)
        }
        return self._signed_request("POST", "/v5/order/create", params)

    def get_book_tickers_completo(self):
        url = f"{self.base_url}/v5/market/tickers"
        try:
            response = self.session.get(url, params={"category": "spot"})
            response.raise_for_status()
            tickers = response.json()["result"]["list"]
            log_info(f"📦 {len(tickers)} tickers recebidos da Bybit")
            return tickers
        except Exception as e:
            log_erro(f"Erro ao obter book tickers da Bybit: {e}")
            return []

    def get_volumes_24h(self):
        return self.get_book_tickers_completo()

    def filtrar_pares_por_volume(self, volume_minimo=0):
        tickers = self.get_book_tickers_completo()
        pares_filtrados = []

        print(f"[DEBUG] Top 10 pares com maior volume (Bybit):")

        validos = []
        for item in tickers:
            try:
                if not all(k in item for k in ["symbol", "bid1Price", "ask1Price", "turnover24h"]):
                    continue

                symbol = item["symbol"]
                bid = float(item["bid1Price"])
                ask = float(item["ask1Price"])
                volume = float(item["turnover24h"])

                validos.append((symbol, volume, bid, ask))
            except Exception as e:
                print(f"[ERRO] ao processar {item.get('symbol', '?')}: {e}")
                continue

        top10 = sorted(validos, key=lambda x: x[1], reverse=True)[:10]

        for symbol, volume, bid, ask in top10:
            print(f"{symbol}: Volume = {volume:.2f} | Bid = {bid:.6f} | Ask = {ask:.6f}")
            pares_filtrados.append({
                "symbol": symbol,
                "bid": bid,
                "ask": ask,
                "volume": volume
            })

        log_info(f"✅ {len(pares_filtrados)} pares exibidos com maiores volumes")
        return pares_filtrados