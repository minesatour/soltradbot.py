import requests
import time
import threading
from flask import Flask, jsonify
from telegram import Bot

# ==========================
# CONFIGURATION
# ==========================

# Set your Telegram Bot credentials
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
CHAT_ID = "your_chat_id"

# Define API endpoints for each exchange
EXCHANGES = {
    "binance": "https://api.binance.com/api/v3/ticker/price?symbol=",
    "kraken": "https://api.kraken.com/0/public/Ticker?pair=",
    "kucoin": "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=",
    "bybit": "https://api.bybit.com/v5/market/tickers?category=spot&symbol=",
    "okx": "https://www.okx.com/api/v5/market/ticker?instId=",
}

# Define coin pairs to track
COINS = ["BTCUSDT", "ETHUSDT", "XRPUSDT"]

# Set minimum profit threshold for alerts
PROFIT_THRESHOLD = 10

# ==========================
# TELEGRAM BOT FUNCTION
# ==========================

def send_telegram_message(message):
    """Send an alert message to Telegram."""
    if TELEGRAM_BOT_TOKEN and CHAT_ID:
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            bot.send_message(chat_id=CHAT_ID, text=message)
        except Exception as e:
            print(f"Telegram Error: {e}")

# ==========================
# PRICE FETCH FUNCTION
# ==========================

def get_price(exchange, symbol):
    """Fetch coin price from an exchange only if API is set."""
    try:
        url = EXCHANGES[exchange] + symbol
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Ensure HTTP 200 response
        data = response.json()

        if exchange == "binance" and "price" in data:
            return float(data['price'])
        elif exchange == "kraken" and "result" in data:
            return float(next(iter(data['result'].values()))['c'][0])
        elif exchange == "kucoin" and "data" in data:
            return float(data['data']['price'])
        elif exchange == "bybit" and "ret_code" in data and data["ret_code"] == 0:
            return float(data['result']['list'][0]['lastPrice'])
        elif exchange == "okx" and "data" in data:
            return float(data['data'][0]['last'])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {exchange}: {e}")
    except (KeyError, IndexError, TypeError) as e:
        print(f"Unexpected data format from {exchange}: {e}")
    return None

# ==========================
# ARBITRAGE FUNCTION
# ==========================

def check_arbitrage():
    """Check for arbitrage opportunities and send Telegram alerts."""
    while True:
        prices = {}
        
        # Fetch prices from all exchanges
        for exchange in EXCHANGES.keys():
            for coin in COINS:
                price = get_price(exchange, coin)
                if price:
                    prices[(exchange, coin)] = price

        # Find arbitrage opportunities
        for coin in COINS:
            coin_prices = {ex: price for (ex, c), price in prices.items() if c == coin}
            
            if len(coin_prices) > 1:
                min_exchange = min(coin_prices, key=coin_prices.get)
                max_exchange = max(coin_prices, key=coin_prices.get)

                min_price = coin_prices[min_exchange]
                max_price = coin_prices[max_exchange]
                profit = max_price - min_price

                if profit >= PROFIT_THRESHOLD:
                    message = (f"🚀 Arbitrage Opportunity 🚀\n"
                               f"{coin}: Buy on {min_exchange} at ${min_price:.2f}, "
                               f"Sell on {max_exchange} at ${max_price:.2f}\n"
                               f"Profit: ${profit:.2f}")
                    
                    print(message)
                    send_telegram_message(message)

        time.sleep(30)  # Check every 30 seconds

# ==========================
# FLASK WEB DASHBOARD
# ==========================

app = Flask(__name__)

@app.route('/arbitrage', methods=['GET'])
def get_arbitrage_opportunities():
    """API Endpoint to get arbitrage opportunities."""
    prices = {}

    # Fetch prices from all exchanges
    for exchange in EXCHANGES.keys():
        for coin in COINS:
            price = get_price(exchange, coin)
            if price:
                prices[(exchange, coin)] = price

    opportunities = []

    # Find arbitrage opportunities
    for coin in COINS:
        coin_prices = {ex: price for (ex, c), price in prices.items() if c == coin}
        
        if len(coin_prices) > 1:
            min_exchange = min(coin_prices, key=coin_prices.get)
            max_exchange = max(coin_prices, key=coin_prices.get)

            min_price = coin_prices[min_exchange]
            max_price = coin_prices[max_exchange]
            profit = max_price - min_price

            if profit >= PROFIT_THRESHOLD:
                opportunities.append({
                    "coin": coin,
                    "buy_from": min_exchange,
                    "buy_price": min_price,
                    "sell_to": max_exchange,
                    "sell_price": max_price,
                    "profit": profit
                })

    return jsonify(opportunities)

# ==========================
# RUN THE SCRIPT
# ==========================

if __name__ == "__main__":
    bot_thread = threading.Thread(target=check_arbitrage, daemon=True)
    bot_thread.start()

    app.run(host='0.0.0.0', port=5000)
