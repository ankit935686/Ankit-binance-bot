#!/usr/bin/env python3
"""
Simple test script for the Binance Futures Trading Bot
"""

import json
import os
from src.basic_bot import BasicBot

def test_connection():
    """Test basic connection to Binance API"""
    print("🔧 Testing Binance Futures Trading Bot...")
    
    # Load configuration
    config_file = 'config.json'
    if not os.path.exists(config_file):
        print("❌ Error: config.json not found")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    api_key = config.get('api_key')
    api_secret = config.get('api_secret')
    testnet = config.get('testnet', True)
    
    if not api_key or not api_secret:
        print("❌ Error: API credentials not found in config.json")
        return False
    
    if api_key == 'YOUR_TESTNET_API_KEY' or api_secret == 'YOUR_TESTNET_API_SECRET':
        print("❌ Error: Please set your actual API credentials in config.json")
        return False
    
    try:
        print(f"📡 Connecting to Binance {'Testnet' if testnet else 'Mainnet'}...")
        bot = BasicBot(api_key, api_secret, testnet=testnet, log_file='test_bot.log')
        
        print("✅ Connection successful!")
        print(f"🔑 API Key: {api_key[:8]}...")
        print(f"🌐 Network: {'Testnet' if testnet else 'Mainnet'}")
        
        # Test account balance
        print("💰 Getting account balance...")
        balance = bot.get_account_balance()
        print(f"✅ Account balance retrieved successfully")
        
        # Test symbol validation
        print("🔍 Testing symbol validation...")
        valid_symbol = bot.validate_symbol('BTCUSDT')
        print(f"✅ Symbol validation working: {valid_symbol}")
        
        print("\n🎉 All tests passed! The bot is ready to use.")
        print("\n📋 Next steps:")
        print("1. Test a small market order: python src/market_orders.py BTCUSDT BUY 0.001")
        print("2. Test limit order: python src/limit_orders.py BTCUSDT SELL 0.001 60000")
        print("3. Use full CLI: python src/main.py --help")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API credentials in config.json")
        print("2. Ensure your API keys have futures trading permissions")
        print("3. Check your internet connection")
        print("4. Verify you're using the correct testnet/mainnet")
        return False

if __name__ == '__main__':
    test_connection()
