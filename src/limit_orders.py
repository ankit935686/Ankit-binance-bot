#!/usr/bin/env python3
"""
Limit Orders CLI - Simple interface for limit orders

This script provides a simple CLI interface for placing limit orders.
For advanced features, use the main.py script.
"""

import sys
import json
import os
from basic_bot import BasicBot

def load_config():
    """Load configuration from config.json"""
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def print_usage():
    print("Usage examples:")
    print("  python limit_orders.py <SYMBOL> <BUY|SELL> <QUANTITY> <PRICE>")
    print("Example:")
    print("  python limit_orders.py BTCUSDT SELL 0.001 60000")
    print("\nNote: Make sure to set your API keys in config.json or use main.py for full functionality")

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print_usage()
        sys.exit(1)

    symbol, side, quantity, price = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    # Load configuration
    config = load_config()
    API_KEY = config.get('api_key', 'YOUR_TESTNET_API_KEY')
    API_SECRET = config.get('api_secret', 'YOUR_TESTNET_API_SECRET')

    if API_KEY == 'YOUR_TESTNET_API_KEY' or API_SECRET == 'YOUR_TESTNET_API_SECRET':
        print("Error: Please set your API keys in config.json")
        print("Or use: python main.py config --set-api-key YOUR_KEY --set-api-secret YOUR_SECRET")
        sys.exit(1)

    bot = BasicBot(API_KEY, API_SECRET, testnet=True, log_file='bot.log')

    try:
        order = bot.place_limit_order(symbol, side, quantity, price)
        print('Limit order placed successfully:')
        print(f"Order ID: {order.get('orderId', 'N/A')}")
        print(f"Symbol: {order.get('symbol', 'N/A')}")
        print(f"Side: {order.get('side', 'N/A')}")
        print(f"Quantity: {order.get('origQty', 'N/A')}")
        print(f"Price: {order.get('price', 'N/A')}")
        print(f"Status: {order.get('status', 'N/A')}")
    except Exception as e:
        print('Failed to place limit order:', e)
        sys.exit(1)
