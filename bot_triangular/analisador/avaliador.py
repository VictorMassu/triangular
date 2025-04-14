# avaliador.py

from bot_triangular.config import SPREAD_MAXIMO
def aplicar_taxa(valor, taxa=0.01):
    return valor * (1 - taxa)

def buscar_preco_ticker(ticker_dict, symbol, tipo, capital):
    from bot_triangular.config import SPREAD_MAXIMO  # <== import movido para dentro da função
    
    dados = ticker_dict[symbol]
    ask = float(dados.get("ask", 0))
    bid = float(dados.get("bid", 0))
    volume = float(dados.get("volume", 0))

    spread = abs(ask - bid) / ((ask + bid) / 2)
    if spread > SPREAD_MAXIMO:
        raise ValueError(f"[SPREAD] Spread alto em {symbol}: {spread:.4f}")

    if tipo == "buy":
        if ask == 0 or volume * ask < capital:
            raise ValueError(f"[LIQUIDEZ] Liquidez insuficiente para comprar {symbol}")
        return ask, volume
    else:
        if bid == 0 or volume < (capital / bid):
            raise ValueError(f"[LIQUIDEZ] Liquidez insuficiente para vender {symbol}")
        return bid, volume

