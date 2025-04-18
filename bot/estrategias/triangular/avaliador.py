from bot.config import TAXA, VALOR_MINIMO_MOEDA
from logs.logs_core.logger import log


def aplicar_taxa(valor, taxa=TAXA):
    return valor * (1 - taxa)


def buscar_preco_com_profundidade(exchange_obj, symbol, tipo, capital, limite=50):
    log.info("Iniciando busca de preço com profundidade", categoria="avaliador", dados={
        "exchange": exchange_obj.get_nome(),
        "symbol": symbol,
        "tipo": tipo,
        "capital": capital,
        "limite": limite
    })

    try:
        book_data = exchange_obj.get_orderbook(symbol, timeout=5)
        book = book_data.get("a" if tipo == "buy" else "b", [])
    except Exception as e:
        log.erro("Erro ao obter book da exchange", categoria="book", dados={
            "exchange": exchange_obj.get_nome(),
            "symbol": symbol,
            "tipo": tipo,
            "erro": str(e)
        })
        raise ValueError(f"[BOOK] Erro ao buscar profundidade para {symbol} na {exchange_obj.get_nome()}: {e}")

    if not book:
        log.erro("Livro de ofertas vazio", categoria="book_vazio", dados={
            "exchange": exchange_obj.get_nome(),
            "symbol": symbol,
            "tipo": tipo
        })
        raise ValueError(f"[BOOK] Livro vazio para {symbol} ({tipo}) na {exchange_obj.get_nome()}")

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
        else:
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
        log.erro("Liquidez insuficiente", categoria="liquidez", dados={
            "exchange": exchange_obj.get_nome(),
            "symbol": symbol,
            "tipo": tipo,
            "capital_restante": capital_restante,
            "capital_total": capital
        })
        raise ValueError(f"[BOOK] Liquidez insuficiente para {tipo} {symbol} na {exchange_obj.get_nome()}")

    preco_medio_ponderado = valor_total / quantidade_total
    log.debug("Preço com profundidade calculado", categoria="avaliador", dados={
        "exchange": exchange_obj.get_nome(),
        "symbol": symbol,
        "tipo": tipo,
        "preco_medio": preco_medio_ponderado,
        "quantidade_total": quantidade_total
    })

    return preco_medio_ponderado, quantidade_total
