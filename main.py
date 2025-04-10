# Estrutura inicial do projeto triangular_bot

# main.py
# Ponto de entrada do sistema

def main():
    from exchanges import binance as exchange  # Pode trocar por outra depois
    from triangular.estrategia import rodar_estrategia

    rodar_estrategia(exchange)

if __name__ == "__main__":
    main()
