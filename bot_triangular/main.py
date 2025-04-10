# Estrutura inicial do projeto triangular_bot

# main.py
# Ponto de entrada do sistema
from bot_triangular.analisador_de_rotas import analisar_oportunidades
from bot_triangular.exchanges.binance.cliente import BinanceExchange

exchange = BinanceExchange()

def main():
    exchange = BinanceExchange()
    analisar_oportunidades(exchange)

if __name__ == "__main__":
    main()