# bot_triangular/analisador/avaliador.py

import requests
from bot_triangular.config import SPREAD_MAXIMO, TAXA, VALOR_MINIMO_MOEDA


def aplicar_taxa(valor, taxa=TAXA):
    """Aplica a taxa de negociação sobre o valor."""
    return valor * (1 - taxa)


def buscar_preco_com_profundidade(symbol, tipo, capital, exchange="binance", limite=50):
    """
    Busca o preço médio ponderado para comprar ou vender uma quantidade com base na profundidade do book.

    - symbol: Par de trading, ex: BTCUSDT
    - tipo: "buy" ou "sell"
    - capital: Valor em USDT (ou moeda base) a ser usado
    - exchange: Por enquanto só suporta "binance"
    - limite: Número de níveis do book (ex: 5, 10, 50, 100)
    """
    if exchange == "binance":
        url = f"https://api.binance.com/api/v3/depth"
        params = {"symbol": symbol, "limit": limite}
    else:
        raise NotImplementedError("Exchange não suportada ainda.")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise ValueError(f"[BOOK] Erro ao buscar profundidade do book para {symbol}: {e}")

    book = data["asks"] if tipo == "buy" else data["bids"]
    if not book:
        raise ValueError(f"[BOOK] Livro vazio para {symbol} - {tipo}")

    quantidade_total = 0
    valor_total = 0
    capital_restante = capital

    for preco_str, qtd_str in book:
        preco = float(preco_str)
        qtd = float(qtd_str)

        if preco < VALOR_MINIMO_MOEDA:
            continue

        if tipo == "buy":
            custo = preco * qtd
            if custo >= capital_restante:
                qtd_utilizada = capital_restante / preco
                valor_total += qtd_utilizada * preco
                quantidade_total += qtd_utilizada
                capital_restante = 0
                break
            else:
                valor_total += custo
                quantidade_total += qtd
                capital_restante -= custo
        else:  # sell
            receita = preco * qtd
            if qtd >= (capital_restante / preco):
                qtd_utilizada = capital_restante / preco
                valor_total += qtd_utilizada * preco
                quantidade_total += qtd_utilizada
                capital_restante = 0
                break
            else:
                valor_total += receita
                quantidade_total += qtd
                capital_restante -= receita

    if capital_restante > 0:
        raise ValueError(f"[BOOK] Liquidez insuficiente para {tipo} {symbol} com {capital:.2f}")

    preco_medio_ponderado = valor_total / quantidade_total
    return preco_medio_ponderado, quantidade_total
