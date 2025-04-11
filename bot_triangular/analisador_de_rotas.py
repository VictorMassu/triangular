import time
import itertools
from datetime import datetime
import json
import os
from time import perf_counter
from bot_triangular.exchanges.binance.cliente import BinanceExchange
from bot_triangular.exchanges.bybit.cliente import BybitExchange
from bot_triangular.utils.logs import log_info, log_erro

# === CONFIGURAÇÕES ===
MOEDA_BASE = "USDT"
VALOR_INICIAL = 100
TAXA = 0.01
LUCRO_MINIMO = 0.0002
SPREAD_MAXIMO = 0.05
LUCRO_IRREALISTA = 500
MOEDAS_BLACKLIST = {"BRL", "ARS", "UAH", "TRY", "VAI", "EUR"}

blacklist_pares = set()

def get_exchange(exchange_type="BINANCE"):
    if exchange_type == "BINANCE":
        ex = BinanceExchange()
        ex.nome = "Binance"
        return ex
    elif exchange_type == "BYBIT":
        ex = BybitExchange()
        ex.nome = "Bybit"
        return ex

def aplicar_taxa(valor):
    return valor * (1 - TAXA)

def converter(capital, preco, tipo):
    if tipo == "buy":
        return capital / preco
    else:
        return capital * preco

def buscar_preco_ticker(ticker_dict, symbol, tipo, capital=VALOR_INICIAL):
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

def salvar_json_lista(caminho, nova_entrada):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r") as f:
                lista = json.load(f)
        except json.JSONDecodeError:
            lista = []
    else:
        lista = []
    lista.append(nova_entrada)
    with open(caminho, "w") as f:
        json.dump(lista, f, indent=4)

def simular_rotas(exchange, volume_minimo=1000):
    pares = exchange.filtrar_pares_por_volume(volume_minimo)
    log_info(f"🔍 {len(pares)} pares com volume > {volume_minimo}")
    ticker_dict = {p['symbol']: p for p in pares}
    todos_pares = set(ticker_dict.keys())

    moedas = set()
    for symbol in todos_pares:
        for m in [symbol[:3], symbol[3:]]:
            if m.isalpha():
                moedas.add(m)

    for m1, m2 in itertools.permutations(moedas, 2):
        if m1 in MOEDAS_BLACKLIST or m2 in MOEDAS_BLACKLIST:
            continue

        start = perf_counter()
        rota = f"{MOEDA_BASE} → {m1} → {m2} → {MOEDA_BASE}"
        par1 = par2 = par3 = None

        try:
            log_info(f"🔄 Testando rota: {rota}")

            par1 = f"{m1}{MOEDA_BASE}" if f"{m1}{MOEDA_BASE}" in todos_pares else f"{MOEDA_BASE}{m1}"
            if par1 not in todos_pares or par1 in blacklist_pares:
                continue
            tipo1 = "buy" if par1.startswith(MOEDA_BASE) else "sell"
            preco1, vol1 = buscar_preco_ticker(ticker_dict, par1, tipo1)
            m1_recebido = aplicar_taxa(converter(VALOR_INICIAL, preco1, tipo1))
            log_info(f"[1] {tipo1.upper()} {VALOR_INICIAL} {MOEDA_BASE} → {m1_recebido} {m1} via {par1} @ {preco1}")

            par2 = f"{m1}{m2}" if f"{m1}{m2}" in todos_pares else f"{m2}{m1}"
            if par2 not in todos_pares or par2 in blacklist_pares:
                continue
            tipo2 = "sell" if par2.startswith(m1) else "buy"
            preco2, vol2 = buscar_preco_ticker(ticker_dict, par2, tipo2, capital=m1_recebido)
            m2_recebido = aplicar_taxa(converter(m1_recebido, preco2, tipo2))
            log_info(f"[2] {tipo2.upper()} {m1_recebido} {m1} → {m2_recebido} {m2} via {par2} @ {preco2}")

            par3 = f"{m2}{MOEDA_BASE}" if f"{m2}{MOEDA_BASE}" in todos_pares else f"{MOEDA_BASE}{m2}"
            if par3 not in todos_pares or par3 in blacklist_pares:
                continue
            tipo3 = "sell" if par3.startswith(m2) else "buy"
            preco3, vol3 = buscar_preco_ticker(ticker_dict, par3, tipo3, capital=m2_recebido)
            final = aplicar_taxa(converter(m2_recebido, preco3, tipo3))
            log_info(f"[3] {tipo3.upper()} {m2_recebido} {m2} → {final} {MOEDA_BASE} via {par3} @ {preco3}")

            lucro_real = final - VALOR_INICIAL
            lucro_pct = (lucro_real / VALOR_INICIAL) * 100
            tempo_execucao = round((perf_counter() - start) * 1000, 2)

            log_info(f"🔎 ROTA FINALIZADA: {rota} | Final = {final:.6f} | Lucro = {lucro_real:.6f} ({lucro_pct:.6f}%)")
            if lucro_pct > LUCRO_IRREALISTA:
                log_info(f"🚨 ALERTA DE LUCRO IRREALISTA (> {LUCRO_IRREALISTA}%): {lucro_pct:.2f}%")

            log_data = {
                "exchange": exchange.nome,
                "rota": rota,
                "timestamp": str(datetime.now()),
                "valor_inicial": VALOR_INICIAL,
                "moedas": [
                    {"par": par1, "tipo_ordem": tipo1, "preco": preco1, "quantidade_recebida": round(m1_recebido, 6), "volume_24h": round(vol1, 2)},
                    {"par": par2, "tipo_ordem": tipo2, "preco": preco2, "quantidade_recebida": round(m2_recebido, 6), "volume_24h": round(vol2, 2)},
                    {"par": par3, "tipo_ordem": tipo3, "preco": preco3, "quantidade_recebida": round(final, 6), "volume_24h": round(vol3, 2)}
                ],
                "valor_final": round(final, 6),
                "lucro_percentual": round(lucro_pct, 6),
                "lucro_real": round(lucro_real, 6),
                "ganho_formatado": f"Valor Inicial: {VALOR_INICIAL} | Valor Final: {round(final, 6)} | Lucro: {round(lucro_pct, 6)}%",
                "spread_maximo_encontrado": round(abs(preco1 - preco1) / preco1 if preco1 else 0, 6),
                "tempo_execucao_ms": tempo_execucao
            }

            salvar_json_lista("log_rotas.json", log_data)

            if lucro_pct >= LUCRO_MINIMO * 100:
                log_info(f"✅ Oportunidade detectada! {rota} | Lucro: {lucro_pct:.4f}%")
                salvar_json_lista("oportunidades.json", log_data)

        except Exception as e:
            log_erro(f"[ERRO] {rota} — {str(e)}")
            for p in [par1, par2, par3]:
                if p: blacklist_pares.add(p)
            continue

def analisar_oportunidades():
    exchanges = [get_exchange("BINANCE"), get_exchange("BYBIT")]
    for ex in exchanges:
        log_info(f"🚀 Iniciando análise na exchange: {ex.nome}")
        simular_rotas(ex, volume_minimo=1000)
