from bot_triangular.exchanges.binance.cliente import BinanceExchange

binance = BinanceExchange()

pares_para_testar = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]

for par in pares_para_testar:
    print(f"\n🔎 Testando par: {par}")
    url = f"{binance.base_url}/v3/ticker/bookTicker"
    response = binance.session.get(url, params={"symbol": par})

    if response.status_code != 200:
        print(f"❌ Erro {response.status_code}: {response.text}")
        continue

    json_data = response.json()
    print(f"📄 Resposta completa: {json_data}")

    ask = json_data.get("askPrice", "N/A")
    bid = json_data.get("bidPrice", "N/A")
    print(f"📈 Ask: {ask} | Bid: {bid}")
