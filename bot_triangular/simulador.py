# bot_triangular/simulador.py
from bot_triangular.utils.logs import log_info
from datetime import datetime
import json
import os

LUCRO_MINIMO = 0.1  # lucro mínimo em %

HISTORICO_PATH = "historico_operacoes.json"

def salvar_historico(dados):
    historico = []
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r") as f:
            try:
                historico = json.load(f)
            except json.JSONDecodeError:
                pass
    historico.append(dados)
    with open(HISTORICO_PATH, "w") as f:
        json.dump(historico, f, indent=2)

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
    detalhes_execucao = []

    for i in range(len(caminho) - 1):
        origem = caminho[i]
        destino = caminho[i + 1]
        (preco_ask, preco_bid), par_usado, direcao = get_preco_bidirecional(exchange, origem, destino)

        if preco_ask is None or preco_bid is None:
            log_info(f"❌ Nenhum par encontrado entre {origem} e {destino}")
            return

        if direcao == "normal":
            saldo_atual /= preco_ask
        else:
            saldo_atual *= preco_bid

        log_info(f"💱 {origem} → {destino} via {par_usado} ({direcao}) @ {preco_ask:.4f}/{preco_bid:.4f} → Novo saldo: {saldo_atual:.6f} {destino}")

        detalhes_execucao.append({
            "par": par_usado,
            "tipo": "compra" if direcao == "normal" else "venda",
            "quantidade": saldo_atual
        })

    lucro_percentual = ((saldo_atual - saldo_inicial) / saldo_inicial) * 100

    if lucro_percentual >= LUCRO_MINIMO:
        log_info(f"✅ Lucro de {lucro_percentual:.4f}% acima do mínimo ({LUCRO_MINIMO}%) — EXECUTANDO 💥")

        for step in detalhes_execucao:
            exchange.executar_ordem(step["par"], step["tipo"], step["quantidade"])

        moeda_final = caminho[-1]
        if moeda_final != moeda_base:
            log_info(f"🔁 Convertendo {moeda_final} de volta para {moeda_base}...")
            exchange.converter_para_usdt(moeda_final)
            if moeda_base != "USDT":
                exchange.converter_para_usdt("USDT")  # Depois implementar conversão para USDC se necessário

        dados = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rota": caminho,
            "valor_inicial": saldo_inicial,
            "valor_final": round(saldo_atual, 6),
            "lucro_percentual": round(lucro_percentual, 4)
        }
        salvar_historico(dados)

        log_info("📋 RESUMO DA OPERAÇÃO")
        log_info(f"🔁 Rota: {' → '.join(caminho)}")
        log_info(f"💰 Valor inicial: {saldo_inicial} {moeda_base}")
        log_info(f"💵 Valor final: {saldo_atual:.6f} {moeda_base}")
        log_info(f"📈 Lucro: {lucro_percentual:.4f}%")
    else:
        log_info(f"⚠️ Lucro {lucro_percentual:.4f}% abaixo do mínimo ({LUCRO_MINIMO}%) — ignorado.")
