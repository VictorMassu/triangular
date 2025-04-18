# bot_triangular/exchanges/base_exchange.py

class BaseExchange:
    """
    Interface padrão para exchanges.
    Toda exchange deve implementar estes métodos com o mesmo tipo de retorno.
    """

    nome = "Abstract"

    def get_nome(self) -> str:
        """
        Retorna o nome da exchange (ex: Binance, Bybit).
        """
        return self.nome

    def get_pares(self) -> list:
        """
        Retorna uma lista de pares disponíveis na exchange.
        Exemplo:
        ["BTCUSDT", "ETHUSDT", ...]
        """
        raise NotImplementedError("Método get_pares() não implementado.")

    def get_precos(self, par: str) -> tuple:
        """
        Retorna uma tupla (ask, bid) com os preços do par.
        Exemplo:
        ("BTCUSDT") -> (60010.0, 59990.0)
        """
        raise NotImplementedError("Método get_precos() não implementado.")

    def consultar_saldo(self, moeda: str) -> float:
        """
        Retorna o saldo disponível da moeda (float).
        Exemplo:
        ("USDT") -> 238.50
        """
        raise NotImplementedError("Método consultar_saldo() não implementado.")

    def executar_ordem(self, par: str, tipo: str, qtd: float, preco: float = None) -> dict:
        """
        Executa uma ordem de mercado.
        tipo: "compra" ou "venda"
        Retorna o dicionário de resposta da API.
        """
        raise NotImplementedError("Método executar_ordem() não implementado.")

    def filtrar_pares_por_volume(self, volume_minimo: float) -> list:
        """
        Retorna uma lista de dicionários com os pares filtrados por volume e com book ativo.
        Formato padrão:
        [
            {"symbol": "BTCUSDT", "bid": 59990.0, "ask": 60010.0},
            ...
        ]
        """
        raise NotImplementedError("Método filtrar_pares_por_volume() não implementado.")
