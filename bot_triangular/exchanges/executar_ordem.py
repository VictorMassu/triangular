# bot_triangular/executar_ordem.py

from bot_triangular.utils.logs import log_info, log_erro


def executar_rota(exchange, rota_info):
    try:
        rota = rota_info['rota']
        log_info(f"🚀 Executando ordem para rota lucrativa: {rota}")

        partes = rota.split(" → ")
        moeda_base, m1, m2, _ = partes

        # Etapa 1: MOEDA_BASE -> m1
        par1 = f"{m1}{moeda_base}" if exchange.get_precos(f"{m1}{moeda_base}")[0] else f"{moeda_base}{m1}"
        tipo1 = "compra" if par1.startswith(moeda_base) else "venda"
        saldo_disponivel = exchange.consultar_saldo(moeda_base)

        if saldo_disponivel < 0.01:
            log_erro("❌ Saldo insuficiente em USDC para iniciar a rota.")
            return False

        qtd1 = saldo_disponivel  # Assume ordem de mercado com todo saldo
        resultado1 = exchange.executar_ordem(par1, tipo1, qtd1)
        if not resultado1:
            log_erro(f"❌ Falha na ordem 1 ({par1})")
            return False

        # Etapa 2: m1 -> m2
        par2 = f"{m1}{m2}" if exchange.get_precos(f"{m1}{m2}")[0] else f"{m2}{m1}"
        tipo2 = "venda" if par2.startswith(m1) else "compra"
        saldo_m1 = exchange.consultar_saldo(m1)

        if saldo_m1 < 0.0001:
            log_erro(f"❌ Saldo insuficiente em {m1} para a segunda etapa.")
            return False

        resultado2 = exchange.executar_ordem(par2, tipo2, saldo_m1)
        if not resultado2:
            log_erro(f"❌ Falha na ordem 2 ({par2})")
            return False

        # Etapa 3: m2 -> MOEDA_BASE
        par3 = f"{m2}{moeda_base}" if exchange.get_precos(f"{m2}{moeda_base}")[0] else f"{moeda_base}{m2}"
        tipo3 = "venda" if par3.startswith(m2) else "compra"
        saldo_m2 = exchange.consultar_saldo(m2)

        if saldo_m2 < 0.0001:
            log_erro(f"❌ Saldo insuficiente em {m2} para a terceira etapa.")
            return False

        resultado3 = exchange.executar_ordem(par3, tipo3, saldo_m2)
        if not resultado3:
            log_erro(f"❌ Falha na ordem 3 ({par3})")
            return False

        log_info("✅ Todas as ordens executadas com sucesso!")
        return True

    except Exception as e:
        log_erro(f"❌ Erro ao executar a rota: {e}")
        return False