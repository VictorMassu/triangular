import time
import hmac
import hashlib
import requests
import json
from bot_triangular.config import API_KEY_BINANCE, SECRET_BINANCE, BASE_URL_BINANCE, AMBIENTE

def gerar_assinatura(secret, query_string):
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def obter_timestamp_sincronizado():
    try:
        response = requests.get(f"{BASE_URL_BINANCE}/v3/time")
        server_time = response.json()["serverTime"]
        return int(server_time)
    except Exception as e:
        print(f"⚠️ Erro ao obter timestamp sincronizado. Usando local: {e}")
        return int(time.time() * 1000)

def consultar_todos_saldos():
    timestamp = obter_timestamp_sincronizado()
    query_string = f"timestamp={timestamp}"
    signature = gerar_assinatura(SECRET_BINANCE, query_string)
    url = f"{BASE_URL_BINANCE}/v3/account?{query_string}&signature={signature}"

    headers = {
        "X-MBX-APIKEY": API_KEY_BINANCE
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    print("📊 Saldos disponíveis:")
    for asset in data['balances']:
        free = float(asset['free'])
        locked = float(asset['locked'])
        if free > 0 or locked > 0:
            print(f"🪙 {asset['asset']}: Livre = {free}, Travado = {locked}")

    return data['balances']

def obter_preco_mercado(par):
    url = f"{BASE_URL_BINANCE}/v3/ticker/price"
    response = requests.get(url, params={"symbol": par})
    response.raise_for_status()
    return float(response.json()["price"])

def enviar_ordem_market_venda(par, quantidade):
    timestamp = obter_timestamp_sincronizado()
    params = {
        "symbol": par,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantidade,
        "timestamp": timestamp
    }

    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    signature = gerar_assinatura(SECRET_BINANCE, query_string)

    url = f"{BASE_URL_BINANCE}/v3/order?{query_string}&signature={signature}"
    headers = {
        "X-MBX-APIKEY": API_KEY_BINANCE
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()
    print("✅ Ordem de conversão enviada com sucesso!")
    print(json.dumps(response.json(), indent=2))

def consultar_saldo(moeda):
    timestamp = obter_timestamp_sincronizado()
    query_string = f"timestamp={timestamp}"
    signature = gerar_assinatura(SECRET_BINANCE, query_string)
    url = f"{BASE_URL_BINANCE}/v3/account?{query_string}&signature={signature}"

    headers = {
        "X-MBX-APIKEY": API_KEY_BINANCE
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    for asset in data['balances']:
        if asset['asset'] == moeda:
            return float(asset['free'])
    return 0.0

def converter_saldo():
    print("🔍 Verificando saldos...")

    if AMBIENTE == "test":
        print("⚠️ Atenção: a consulta de saldo só funciona se a chave for válida na testnet.")
    consultar_todos_saldos()

    moeda = input("\n🪙 Qual moeda você quer converter para USDT? (ex: BTC): ").strip().upper()
    par = moeda + "USDT"
    print(f"\n🔁 Par de conversão assumido: {par}")

    saldo = consultar_saldo(moeda)
    print(f"💰 Saldo disponível de {moeda}: {saldo}")

    if saldo == 0.0:
        print("❌ Saldo insuficiente.")
        return

    preco = obter_preco_mercado(par)
    print(f"📈 Preço atual de {moeda} para USDT: {preco:.2f}")

    confirmar = input(f"⚠️ Deseja converter {saldo} {moeda} para USDT agora? (s/n): ").strip().lower()
    if confirmar == "s":
        enviar_ordem_market_venda(par, saldo)
    else:
        print("❌ Conversão cancelada.")

if __name__ == "__main__":
    converter_saldo()
