# exchanges/binance/cliente.py
from ..base_exchange import BaseExchange

class BinanceExchange(BaseExchange):
    def get_pares(self):
        # Implementa busca de pares na Binance Testnet
        pass

    def get_precos(self, par):
        # Busca book com ask e bid
        pass

    def executar_ordem(self, par, tipo, qtd):
        # Cria ordem na Testnet
        pass

    def consultar_saldo(self, moeda):
        # Consulta saldo de moeda
        pass
