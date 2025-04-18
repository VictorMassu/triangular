import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from bot.exchanges.base_exchange import BaseExchange
from logs.logs_core.logger import log
from bot.config import (
    API_KEY_BYBIT, SECRET_BYBIT, BASE_URL_BYBIT,
    VOLUME_MINIMO_PARA_ANALISE, SPREAD_MAXIMO,
    VALOR_MINIMO_MOEDA, MOEDAS_BLACKLIST
)


class BybitExchange(BaseExchange):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-BYBIT-API-KEY": API_KEY_BYBIT})
        self.base_url = BASE_URL_BYBIT
        self.nome = "Bybit"
        log.info("BybitExchange inicializado com sucesso", categoria="bybit")

    def get_nome(self) -> str:
        return self.nome

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
            log.erro("Erro na requisição assinada", categoria="bybit", dados={"path": path, "erro": str(e)})
            return None

    def get_pares(self) -> list:
        log.info("Buscando pares disponíveis", categoria="bybit")
        try:
            url = f"{self.base_url}/v5/market/instruments-info"
            response = self.session.get(url, params={"category": "spot"})
            response.raise_for_status()
            data = response.json().get("result", {}).get("list", [])
            pares = [s["symbol"] for s in data if s["status"] == "Trading"]
            log.debug("Pares obtidos com sucesso", categoria="bybit", dados={"quantidade": len(pares)})
            return pares
        except Exception as e:
            log.erro("Erro ao obter pares", categoria="bybit", dados={"erro": str(e)})
            return []

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
            log.erro("Erro ao obter orderbook", categoria="bybit", dados={"symbol": symbol, "erro": str(e)})
            return {}

    def get_precos(self, par: str) -> tuple:
        log.info(f"Consultando preços do par {par}", categoria="bybit")
        try:
            book = self.get_orderbook(par)
            asks = book.get("a", [])
            bids = book.get("b", [])
            if not asks or not bids:
                raise ValueError("Asks ou Bids vazios.")
            ask = float(asks[0][0])
            bid = float(bids[0][0])
            log.debug("Preços obtidos", categoria="bybit", dados={"par": par, "ask": ask, "bid": bid})
            return ask, bid
        except Exception as e:
            log.erro("Erro ao obter preços", categoria="bybit", dados={"par": par, "erro": str(e)})
        return None, None

    def consultar_saldo(self, moeda: str) -> float:
        log.info(f"Consultando saldo da moeda {moeda}", categoria="bybit")
        path = "/v5/account/wallet-balance"
        data = self._signed_request("GET", path, {"accountType": "UNIFIED"})
        if not data:
            return 0.0

        try:
            lista_moedas = data.get("result", {}).get("list", [])[0].get("coin", [])
            for b in lista_moedas:
                if b["coin"].upper() == moeda.upper():
                    saldo = float(b["availableToWithdraw"])
                    log.debug("Saldo encontrado", categoria="bybit", dados={"moeda": moeda, "saldo": saldo})
                    return saldo
            log.info(f"Moeda {moeda} não encontrada", categoria="bybit")
        except Exception as e:
            log.erro("Erro ao processar saldo", categoria="bybit", dados={"erro": str(e)})
        return 0.0

    def executar_ordem(self, par: str, tipo: str, qtd: float, preco: float = None) -> dict:
        log.info(f"Executando ordem de {tipo} no par {par}", categoria="bybit", dados={"qtd": qtd})
        side = "Buy" if tipo.lower() == "compra" else "Sell"
        params = {
            "category": "spot",
            "symbol": par,
            "side": side,
            "orderType": "Market",
            "qty": str(qtd)
        }
        resultado = self._signed_request("POST", "/v5/order/create", params)
        if resultado:
            log.debug("Ordem executada", categoria="bybit", dados=resultado)
        else:
            log.erro("Falha ao executar ordem", categoria="bybit", dados=params)
        return resultado

    def filtrar_pares_por_volume(self, volume_minimo: float) -> list:
        log.info("Iniciando filtro de pares por volume", categoria="bybit", dados={"volume_minimo": volume_minimo})
        try:
            url = f"{self.base_url}/v5/market/tickers"
            response = self.session.get(url, params={"category": "spot"})
            response.raise_for_status()
            tickers = response.json().get("result", {}).get("list", [])
        except Exception as e:
            log.erro("Erro ao buscar tickers", categoria="bybit", dados={"erro": str(e)})
            return []

        pares_filtrados = []

        for ticker in tickers:
            try:
                symbol = ticker.get("symbol")
                bid_str = ticker.get("bid1Price")
                ask_str = ticker.get("ask1Price")
                volume_usd_str = ticker.get("turnover24h", "0")

                # Converte e valida
                bid = float(bid_str) if bid_str else 0
                ask = float(ask_str) if ask_str else 0
                volume = float(volume_usd_str)
                moeda_base = symbol.replace("USDT", "").replace("USDC", "")

                if (
                    bid <= 0 or ask <= 0 or volume < volume_minimo
                    or any(x in symbol for x in MOEDAS_BLACKLIST)
                    or bid < VALOR_MINIMO_MOEDA
                ):
                    continue

                pares_filtrados.append({
                    "symbol": symbol,
                    "bid": bid,
                    "ask": ask,
                    "volume": volume,
                    "exchange": self.get_nome()
                })

            except Exception as e:
                log.erro("Erro ao processar ticker", categoria="bybit", dados={"ticker": ticker, "erro": str(e)})
                continue

        # 🧠 Ordena do maior para o menor volume
        pares_filtrados.sort(key=lambda x: x["volume"], reverse=True)

        log.info(f"Pares válidos encontrados: {len(pares_filtrados)}", categoria="bybit")
        return pares_filtrados
