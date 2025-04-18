# bot/estrategias/base_estrategias.py

class BaseStrategy:
    """
    Interface base para todas as estratégias do robô de arbitragem.
    Cada estratégia deve implementar obrigatoriamente:
    - analisar(): para identificar oportunidades
    - executar(): para executar a operação (mesmo que esteja em branco inicialmente)
    """

    def analisar(self):
        raise NotImplementedError("A estratégia precisa implementar o método 'analisar'.")

    def executar(self):
        raise NotImplementedError("A estratégia precisa implementar o método 'executar'.")
