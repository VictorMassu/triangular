# triangular/simulador.py
from bot_triangular.utils.logs import log_info

LUCRO_MINIMO = 0.1  # lucro mínimo aceitável em porcentagem para considerar a oportunidade viável

def get_preco_bidirecional(exchange, moeda_a, moeda_b):
    par_normal = moeda_a + moeda_b
    preco_ask, preco_bid = exchange.get_precos(par_normal)
    if preco_ask and preco_bid:
        return (preco_ask, preco_bid), par_normal, "normal"

    par_invertido = moeda_b + moeda_a
    preco_ask, preco_bid = exchange.get_precos(par_invertido)
    if preco_ask and preco_bid:
        return (preco_ask, preco_bid), par_invertido, "invertido"

    return (None, None), None, None

def simular_rotas(exchange, oportunidade):
    log_info(f"🔄 Iniciando simulação da oportunidade: {oportunidade}")

    moeda_base = oportunidade['base']
    caminho = oportunidade['rota']
    saldo_inicial = 100
    saldo_atual = saldo_inicial

    for i in range(len(caminho) - 1):
        moeda_origem = caminho[i]
        moeda_destino = caminho[i + 1]
        (preco_ask, preco_bid), par_usado, direcao = get_preco_bidirecional(exchange, moeda_origem, moeda_destino)

        if preco_ask is None or preco_bid is None:
            log_info(f"❌ Nenhum par encontrado entre {moeda_origem} e {moeda_destino}")
            return

        if direcao == "normal":
            saldo_atual /= preco_ask
        elif direcao == "invertido":
            saldo_atual *= preco_bid
        else:
            log_info("❌ Erro inesperado na identificação da direção do par")
            return

        log_info(f"💱 {moeda_origem} → {moeda_destino} via {par_usado} ({direcao}) @ {preco_ask:.4f}/{preco_bid:.4f} → Novo saldo: {saldo_atual:.6f} {moeda_destino}")

    lucro_percentual = ((saldo_atual - saldo_inicial) / saldo_inicial) * 100
    if lucro_percentual >= LUCRO_MINIMO:
        log_info(f"✅ Simulação finalizada. Lucro: {lucro_percentual:.4f}% — OPORTUNIDADE VIÁVEL! 💰")
    else:
        log_info(f"⚠️ Simulação finalizada. Lucro: {lucro_percentual:.4f}% — abaixo do mínimo de {LUCRO_MINIMO}%")
