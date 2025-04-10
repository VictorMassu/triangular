# triangular/simulador.py
from utils.logs import log_info

def simular_rotas(exchange, oportunidade):
    log_info(f"🔄 Iniciando simulação da oportunidade: {oportunidade}")

    moeda_base = oportunidade['base']
    caminho = oportunidade['rota']  # ex: ['USDT', 'ETH', 'BTC', 'USDT']
    saldo_inicial = 100  # simulação com 100 unidades da moeda base

    saldo_atual = saldo_inicial

    for i in range(len(caminho) - 1):
        par = caminho[i] + caminho[i + 1]
        try:
            preco_compra, preco_venda = exchange.get_precos(par)
        except:
            log_info(f"❌ Falha ao obter preços para {par}")
            return

        if preco_compra is None or preco_venda is None:
            log_info(f"❌ Preços não disponíveis para o par {par}")
            return

        # Vamos supor que compramos sempre no ask (pior caso)
        saldo_atual = saldo_atual / preco_compra
        log_info(f"💱 {caminho[i]} → {caminho[i+1]} via {par} @ {preco_compra:.4f} → Novo saldo: {saldo_atual:.6f} {caminho[i+1]}")

    lucro_percentual = ((saldo_atual - saldo_inicial) / saldo_inicial) * 100
    log_info(f"✅ Simulação finalizada. Saldo inicial: {saldo_inicial} {moeda_base}, Final: {saldo_atual:.6f} {moeda_base}, Lucro: {lucro_percentual:.4f}%")
