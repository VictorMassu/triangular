# Estrutura inicial do projeto triangular_bot

# main.py
# Ponto de entrada do sistema
from bot_triangular.estrategia import rodar_estrategia
from bot_triangular.exchanges import binance as exchange

def main():

    rodar_estrategia(exchange)

if __name__ == "__main__":
    main()
