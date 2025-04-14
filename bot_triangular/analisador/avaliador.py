# bot_triangular/analisador/avaliador.py

from bot_triangular.config import SPREAD_MAXIMO, TAXA, VALOR_MINIMO_MOEDA

def aplicar_taxa(valor, taxa=TAXA):
    """Aplica a taxa de negociação sobre o valor."""
    return valor * (1 - taxa)

def buscar_preco_ticker(ticker_dict, symbol, tipo, capital):
    """
    Busca o preço (ask ou bid) e valida a liquidez do par, considerando o spread.
    """
    dados = ticker_dict[symbol]
    ask = float(dados.get("ask", 0))
    bid = float(dados.get("bid", 0))
    volume = float(dados.get("volume", 0))

    # Validação de spread
    spread = abs(ask - bid) / ((ask + bid) / 2) if (ask + bid) != 0 else 1
    if spread > SPREAD_MAXIMO:
        raise ValueError(f"[SPREAD] Spread alto em {symbol}: {spread:.4f}")

    # Verificação de tipo de operação
    if tipo == "buy":
        if ask == 0 or volume * ask < capital:
            raise ValueError(f"[LIQUIDEZ] Liquidez insuficiente para comprar {symbol}")
        if ask < VALOR_MINIMO_MOEDA:
            raise ValueError(f"[PREÇO] Preço muito baixo para {symbol} (ask: {ask})")
        return ask, volume
    else:
        if bid == 0 or volume < (capital / bid):
            raise ValueError(f"[LIQUIDEZ] Liquidez insuficiente para vender {symbol}")
        if bid < VALOR_MINIMO_MOEDA:
            raise ValueError(f"[PREÇO] Preço muito baixo para {symbol} (bid: {bid})")
        return bid, volume
