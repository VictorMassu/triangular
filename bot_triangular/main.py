# Estrutura inicial do projeto triangular_bot

# main.py
# Ponto de entrada do sistema
from bot_triangular.analisador_de_rotas import analisar_oportunidades
from bot_triangular.exchanges.binance.cliente import BinanceExchange

exchange = BinanceExchange()

def main():
    exchange = BinanceExchange()
    analisar_oportunidades(exchange)
     # Etapa opcional: conversão para USDT
    confirmar = input("\n💱 Deseja converter alguma moeda para USDC? (ex: BTC ou n para pular): ").strip().upper()
    if confirmar and confirmar != "N":
        exchange.converter_para_usdt(confirmar)

if __name__ == "__main__":
    main()