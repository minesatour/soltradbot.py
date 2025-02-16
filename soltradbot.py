import sys
import requests
import json
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, 
    QMessageBox, QDoubleSpinBox, QHBoxLayout, QFormLayout, QComboBox, QCheckBox
)
from PyQt6.QtCore import QThread

class SolExchangeAPI:
    """Handles API requests for placing trades."""
    
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.solexchange.com"

    def place_order(self, wallet_address, symbol, side, amount, price=None):
        """Places a buy or sell order."""
        url = f"{self.base_url}/api/v1/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "wallet_address": wallet_address,
            "symbol": symbol,
            "side": side,
            "amount": amount
        }
        if price:
            payload["price"] = price

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

class MemecoinScanner(QWidget):
    """Main application for scanning and trading Solana memecoins."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Solana Memecoin Trading Bot")
        self.setGeometry(100, 100, 600, 500)
        self.layout = QVBoxLayout()

        # User Input Fields
        self.form_layout = QFormLayout()

        self.wallet_input = QLineEdit()
        self.api_key_input = QLineEdit()
        self.api_secret_input = QLineEdit()
        self.max_trade_input = QDoubleSpinBox()
        self.max_trade_input.setRange(1, 1000)
        self.stop_loss_input = QDoubleSpinBox()
        self.stop_loss_input.setRange(1, 50)
        self.take_profit_input = QDoubleSpinBox()
        self.take_profit_input.setRange(5, 100)
        self.trade_frequency_input = QComboBox()
        self.trade_frequency_input.addItems(["10 minutes", "1 hour", "Daily"])
        self.safe_mode_checkbox = QCheckBox("Enable Safe Mode")

        self.form_layout.addRow("Wallet Address:", self.wallet_input)
        self.form_layout.addRow("API Key:", self.api_key_input)
        self.form_layout.addRow("API Secret:", self.api_secret_input)
        self.form_layout.addRow("Max Trade Per Coin (£):", self.max_trade_input)
        self.form_layout.addRow("Stop Loss %:", self.stop_loss_input)
        self.form_layout.addRow("Take Profit %:", self.take_profit_input)
        self.form_layout.addRow("Trade Frequency:", self.trade_frequency_input)
        self.form_layout.addRow(self.safe_mode_checkbox)

        self.layout.addLayout(self.form_layout)

        # Buttons
        self.scan_button = QPushButton("Scan for Memecoins")
        self.scan_button.clicked.connect(self.start_scan)
        self.layout.addWidget(self.scan_button)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.layout.addWidget(self.result_box)

        self.setLayout(self.layout)
        self.scan_thread = None

    def start_scan(self):
        """Starts a new scan thread."""
        if self.scan_thread is None or not self.scan_thread.isRunning():
            self.scan_button.setEnabled(False)
            self.scan_thread = ScanThread(self)
            self.scan_thread.start()

    def get_new_sol_tokens(self):
        """Fetch new Solana tokens from CoinGecko."""
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "category": "solana-ecosystem",
            "order": "market_cap_asc",
            "per_page": 50,
            "page": 1
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return [token for token in response.json() if token.get('market_cap') and token['market_cap'] < 50000]
        except requests.RequestException:
            return []

    def get_dex_screener_data(self):
        """Fetch trading pairs from DEX Screener."""
        url = "https://api.dexscreener.com/latest/dex/search?q=sol"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get("pairs", [])
        except requests.RequestException:
            return []

    def filter_potential_coins(self):
        """Identify new memecoins based on market conditions."""
        new_tokens = self.get_new_sol_tokens()
        dex_data = self.get_dex_screener_data()

        potential_coins = []
        for token in new_tokens:
            token_symbol = token['symbol'].lower()
            for pair in dex_data:
                base_token = pair.get('baseToken', {})
                if base_token.get('symbol', '').lower() == token_symbol:
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                    volume = float(pair.get('volume', {}).get('h24', 0))

                    if liquidity > 50000 and volume > 100000:
                        potential_coins.append({
                            "name": token['name'],
                            "symbol": token['symbol'],
                            "price": float(pair['priceUsd']),
                            "liquidity": liquidity,
                            "volume": volume,
                            "pair_url": pair.get("url")
                        })
        return potential_coins

    def scan_coins(self):
        """Trigger scan and execute trades."""
        coins = self.filter_potential_coins()
        self.result_box.clear()
        if coins:
            for coin in coins:
                self.result_box.append(f"{coin['name']} ({coin['symbol']}): ${coin['price']}")
                self.trade_coin(coin)
        else:
            self.result_box.append("No new memecoins found.")

    def trade_coin(self, coin):
        """Handles trade execution."""
        wallet_address = self.wallet_input.text()
        api_key = self.api_key_input.text()
        api_secret = self.api_secret_input.text()
        max_trade = self.max_trade_input.value()
        stop_loss = self.stop_loss_input.value()
        take_profit = self.take_profit_input.value()

        if not wallet_address or not api_key or not api_secret or max_trade <= 0:
            self.result_box.append("Invalid trade settings.")
            return

        trade_amount = min(max_trade, coin["price"])  

        api_client = SolExchangeAPI(api_key, api_secret)
        order_response = api_client.place_order(wallet_address, coin['symbol'], "buy", trade_amount)

        if order_response and "order_id" in order_response:
            self.result_box.append(f"Bought {coin['name']} at ${coin['price']}")
        else:
            self.result_box.append("Trade failed.")

    def scan_finished(self):
        self.scan_button.setEnabled(True)

class ScanThread(QThread):
    """Handles scanning in a separate thread."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        self.parent.scan_coins()
        self.parent.scan_finished()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemecoinScanner()
    window.show()
    sys.exit(app.exec())
