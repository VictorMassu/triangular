# exchanges/base_exchange.py
class BaseExchange:
    def get_pares(self): raise NotImplementedError
    def get_precos(self, par): raise NotImplementedError
    def executar_ordem(self, par, tipo, qtd): raise NotImplementedError
    def consultar_saldo(self, moeda): raise NotImplementedError