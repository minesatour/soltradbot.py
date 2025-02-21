🚀 Crypto Arbitrage Bot

📌 Overview

This script is a real-time crypto arbitrage bot that monitors multiple exchanges for price differences and notifies you via Telegram when a profitable trade is found. 
It also includes a web API dashboard to fetch arbitrage opportunities on demand.

🛠️ Features

✔ Real-Time Price Monitoring – Fetches prices from multiple exchanges. ✔ Arbitrage Detection – Identifies profit opportunities between exchanges. 
✔ Telegram Alerts – Sends notifications when profit is detected. ✔ Web Dashboard API – Access arbitrage data in JSON format. 
✔ Error Handling – Prevents crashes and handles API failures gracefully. ✔ Optimized Threading – Runs smoothly in the background. ✔ Lightweight & Fast – Efficiently scans markets without excessive load.

📌 Supported Exchanges
Binance
Kraken
KuCoin
Bybit
OKX

📌 Tracked Coin Pairs
BTC/USDT
ETH/USDT
XRP/USDT

🚀 Installation & Setup
1️⃣ Install Dependencies
Ensure you have Python installed, then install the required packages:

pip install requests flask python-telegram-bot 

2️⃣ Set Up Telegram Bot
Create a Telegram bot via BotFather and get the BOT TOKEN.

Get your Chat ID from @userinfobot.

Set your environment variables:

export TELEGRAM_BOT_TOKEN="your_telegram_bot_token" export CHAT_ID="your_chat_id" 

3️⃣ Run the Script

python script.py 

🔔 How It Works
The bot fetches real-time prices from all supported exchanges.
It checks for arbitrage opportunities where the profit is greater than $10.
If an opportunity is found, it sends a Telegram alert with details.
You can also fetch arbitrage data via the web API.

🌍 Web API
You can access arbitrage data in JSON format:
http://localhost:5000/arbitrage 

Example response:
[ { "coin": "BTCUSDT", "buy_from": "binance", "buy_price": 42000.00, "sell_to": "kraken", "sell_price": 42150.00, "profit": 150.00 } ] 

🤖 Example Telegram Alert
🚀 Arbitrage Opportunity 🚀 BTCUSDT: Buy on Binance at $42,000.00, Sell on Kraken at $42,150.00 Profit: $150.00 
🛠️ Configuration
You can edit the script to change:
Tracked Coins (COINS variable)
Minimum Profit Threshold (PROFIT_THRESHOLD variable)

⚠️ Disclaimer
This script is for educational purposes only.
Trading involves risk; use at your own discretion.
Ensure compliance with exchange terms before trading.


