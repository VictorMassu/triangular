def construir_par(m1, m2, todos_pares):
    if f"{m1}{m2}" in todos_pares:
        return f"{m1}{m2}"
    elif f"{m2}{m1}" in todos_pares:
        return f"{m2}{m1}"
    return None

def gerar_ticker_dict(pares_raw, log=None):
    ticker_dict = {}
    for p in pares_raw:
        try:
            ask = float(p.get('ask', 0))
            bid = float(p.get('bid', 0))
            if ask <= 0 or bid <= 0:
                if log:
                    log.debug("Preço inválido encontrado", categoria="preco_zero", dados=p, id=p.get("symbol"))
                continue
            ticker_dict[p['symbol']] = p
        except Exception:
            if log:
                log.erro("Erro ao processar par", categoria="preco_parse_fail", dados=p, id=p.get("symbol"))
    return ticker_dict
