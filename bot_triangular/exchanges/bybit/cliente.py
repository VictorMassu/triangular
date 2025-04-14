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
            log_erro(f"❌ Erro na requisição assinada (Bybit): {e}")
            return None

    def get_symbols(self):
        try:
            url = f"{self.base_url}/v5/market/instruments-info"
            response = self.session.get(url, params={"category": "spot"})
            response.raise_for_status()
            return [s["symbol"] for s in response.json().get("result", {}).get("list", []) if s["status"] == "Trading"]
        except Exception as e:
            log_erro(f"❌ Erro ao obter symbols da Bybit: {e}")
            return []

    def get_pares(self):
        return self.get_symbols()

    def get_orderbook(self, symbol, timeout=5):
        try:
            url = f"{self.base_url}/v5/market/orderbook"
            response = self.session.get(
                url,
                params={"symbol": symbol, "category": "spot", "limit": 1},
                timeout=timeout
            )
            response.raise_for_status()
            return response.json().get("result", {})
        except Exception as e:
            log_erro(f"❌ Erro ao obter orderbook do par {symbol}: {e}")
            return {}

    def get_precos(self, par):
        try:
            orderbook = self.get_orderbook(par)
            ask = float(orderbook.get("a", [])[0][1])
            bid = float(orderbook.get("b", [])[0][1])
            return ask, bid
        except Exception as e:
            log_erro(f"❌ Erro ao obter preços do par {par}: {e}")
            return None, None

    def consultar_saldo(self, moeda):
        path = "/v5/account/wallet-balance"
        data = self._signed_request("GET", path, {"accountType": "UNIFIED"})
        if not data:
            return 0.0

        balances = data.get("result", {}).get("list", [])[0].get("coin", [])
        for b in balances:
            if b["coin"].upper() == moeda.upper():
                saldo = float(b["availableToWithdraw"])
                log_info(f"💰 Bybit | Saldo disponível em {moeda}: {saldo}")
                return saldo
        log_info(f"⚠️ Bybit | Moeda {moeda} não encontrada.")
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

    def filtrar_pares_por_volume(self, volume_minimo=10000):
        symbols = self.get_symbols()
        pares_filtrados = []

        for symbol in symbols:
            try:
                book = self.get_orderbook(symbol)
                bids = book.get("b", [])
                asks = book.get("a", [])
                if not bids or not asks:
                    continue
                best_bid = float(bids[0][1])
                best_ask = float(asks[0][1])
                if best_bid > 0 and best_ask > 0:
                    pares_filtrados.append({
                        "symbol": symbol,
                        "bid": best_bid,
                        "ask": best_ask
                    })
            except Exception as e:
                log_erro(f"Erro ao filtrar par {symbol}: {e}")
                continue

            time.sleep(0.2)  # Evita excesso de requisições

        log_info(f"✅ Bybit | {len(pares_filtrados)} pares válidos encontrados com book ativo.")
        return pares_filtrados
