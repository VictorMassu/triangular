from bot_triangular.analisador.analisador_de_rotas import analisar_oportunidades
from bot_triangular.analisador.blacklist_manager import init_blacklists

def main():
    init_blacklists()
    analisar_oportunidades()

if __name__ == "__main__":
    main()
