#!/usr/bin/env python3
"""
Binance Futures Trading Bot - Main CLI Interface

This is the main entry point for the Binance Futures trading bot.
It provides a comprehensive CLI interface for all order types and strategies.
"""

import sys
import argparse
import json
import os
from typing import Dict, Any, Optional

# Import bot components
from basic_bot import BasicBot
from advanced.stop_limit import StopLimitOrders
from advanced.oco import OCOOrders
from advanced.twap import TWAPStrategy
from advanced.grid_orders import GridOrders


class BinanceTradingBot:
    """Main trading bot class that orchestrates all order types."""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, log_file: str = 'bot.log'):
        """
        Initialize the trading bot with all components.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet (True) or mainnet (False)
            log_file: Path to log file
        """
        self.bot = BasicBot(api_key, api_secret, testnet, log_file)
        self.stop_limit = StopLimitOrders(self.bot)
        self.oco = OCOOrders(self.bot)
        self.twap = TWAPStrategy(self.bot)
        self.grid = GridOrders(self.bot)
        
        self.logger = self.bot.logger
    
    def market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Place a market order."""
        return self.bot.place_market_order(symbol, side, quantity)
    
    def limit_order(self, symbol: str, side: str, quantity: float, price: float, 
                   time_in_force: str = 'GTC') -> Dict[str, Any]:
        """Place a limit order."""
        return self.bot.place_limit_order(symbol, side, quantity, price, time_in_force)
    
    def stop_limit_order(self, symbol: str, side: str, quantity: float, 
                        stop_price: float, limit_price: float, 
                        time_in_force: str = 'GTC') -> Dict[str, Any]:
        """Place a stop-limit order."""
        return self.stop_limit.place_stop_limit_order(symbol, side, quantity, stop_price, limit_price, time_in_force)
    
    def stop_market_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Dict[str, Any]:
        """Place a stop-market order."""
        return self.stop_limit.place_stop_market_order(symbol, side, quantity, stop_price)
    
    def take_profit_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> Dict[str, Any]:
        """Place a take-profit order."""
        return self.stop_limit.place_take_profit_order(symbol, side, quantity, stop_price)
    
    def oco_order(self, symbol: str, side: str, quantity: float, 
                 take_profit_price: float, stop_loss_price: float, 
                 time_in_force: str = 'GTC') -> Dict[str, Any]:
        """Place an OCO order."""
        return self.oco.place_oco_order(symbol, side, quantity, take_profit_price, stop_loss_price, time_in_force)
    
    def twap_order(self, symbol: str, side: str, total_quantity: float, 
                  duration_minutes: int, num_slices: int = None,
                  order_type: str = 'MARKET', price: float = None) -> Dict[str, Any]:
        """Execute a TWAP order."""
        return self.twap.execute_twap_order(symbol, side, total_quantity, duration_minutes, num_slices, order_type, price)
    
    def grid_strategy(self, symbol: str, side: str, quantity_per_order: float,
                     lower_price: float, upper_price: float, num_orders: int,
                     grid_type: str = 'LINEAR') -> Dict[str, Any]:
        """Create and execute a grid strategy."""
        grid_config = self.grid.create_grid_strategy(symbol, side, quantity_per_order, lower_price, upper_price, num_orders, grid_type)
        return self.grid.execute_grid_orders(grid_config['grid_id'])
    
    def dca_grid(self, symbol: str, side: str, total_quantity: float,
                start_price: float, price_decrement: float, num_orders: int) -> Dict[str, Any]:
        """Create and execute a DCA grid strategy."""
        grid_config = self.grid.create_dca_grid(symbol, side, total_quantity, start_price, price_decrement, num_orders)
        return self.grid.execute_grid_orders(grid_config['grid_id'])
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order."""
        return self.bot.cancel_order(symbol, order_id)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Get order status."""
        return self.bot.get_order_status(symbol, order_id)
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        return self.bot.get_account_balance()


def load_config(config_file: str = 'config.json') -> Dict[str, Any]:
    """Load configuration from file."""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, Any], config_file: str = 'config.json'):
    """Save configuration to file."""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot')
    
    # Global options
    parser.add_argument('--api-key', help='Binance API key')
    parser.add_argument('--api-secret', help='Binance API secret')
    parser.add_argument('--testnet', action='store_true', default=True, help='Use testnet (default: True)')
    parser.add_argument('--mainnet', action='store_true', help='Use mainnet (overrides testnet)')
    parser.add_argument('--log-file', default='bot.log', help='Log file path')
    parser.add_argument('--config', default='config.json', help='Configuration file')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Market order
    market_parser = subparsers.add_parser('market', help='Place market order')
    market_parser.add_argument('symbol', help='Trading symbol (e.g., BTCUSDT)')
    market_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    market_parser.add_argument('quantity', type=float, help='Order quantity')
    
    # Limit order
    limit_parser = subparsers.add_parser('limit', help='Place limit order')
    limit_parser.add_argument('symbol', help='Trading symbol')
    limit_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    limit_parser.add_argument('quantity', type=float, help='Order quantity')
    limit_parser.add_argument('price', type=float, help='Order price')
    limit_parser.add_argument('--time-in-force', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    
    # Stop-limit order
    stop_limit_parser = subparsers.add_parser('stop-limit', help='Place stop-limit order')
    stop_limit_parser.add_argument('symbol', help='Trading symbol')
    stop_limit_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    stop_limit_parser.add_argument('quantity', type=float, help='Order quantity')
    stop_limit_parser.add_argument('stop_price', type=float, help='Stop price')
    stop_limit_parser.add_argument('limit_price', type=float, help='Limit price')
    stop_limit_parser.add_argument('--time-in-force', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    
    # Stop-market order
    stop_market_parser = subparsers.add_parser('stop-market', help='Place stop-market order')
    stop_market_parser.add_argument('symbol', help='Trading symbol')
    stop_market_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    stop_market_parser.add_argument('quantity', type=float, help='Order quantity')
    stop_market_parser.add_argument('stop_price', type=float, help='Stop price')
    
    # Take-profit order
    take_profit_parser = subparsers.add_parser('take-profit', help='Place take-profit order')
    take_profit_parser.add_argument('symbol', help='Trading symbol')
    take_profit_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    take_profit_parser.add_argument('quantity', type=float, help='Order quantity')
    take_profit_parser.add_argument('stop_price', type=float, help='Take-profit price')
    
    # OCO order
    oco_parser = subparsers.add_parser('oco', help='Place OCO order')
    oco_parser.add_argument('symbol', help='Trading symbol')
    oco_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    oco_parser.add_argument('quantity', type=float, help='Order quantity')
    oco_parser.add_argument('take_profit_price', type=float, help='Take-profit price')
    oco_parser.add_argument('stop_loss_price', type=float, help='Stop-loss price')
    oco_parser.add_argument('--time-in-force', default='GTC', choices=['GTC', 'IOC', 'FOK'], help='Time in force')
    
    # TWAP order
    twap_parser = subparsers.add_parser('twap', help='Execute TWAP order')
    twap_parser.add_argument('symbol', help='Trading symbol')
    twap_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    twap_parser.add_argument('total_quantity', type=float, help='Total quantity')
    twap_parser.add_argument('duration_minutes', type=int, help='Duration in minutes')
    twap_parser.add_argument('--num-slices', type=int, help='Number of slices (auto-calculated if not provided)')
    twap_parser.add_argument('--order-type', default='MARKET', choices=['MARKET', 'LIMIT'], help='Order type')
    twap_parser.add_argument('--price', type=float, help='Price for limit orders')
    
    # Grid strategy
    grid_parser = subparsers.add_parser('grid', help='Create grid strategy')
    grid_parser.add_argument('symbol', help='Trading symbol')
    grid_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    grid_parser.add_argument('quantity_per_order', type=float, help='Quantity per order')
    grid_parser.add_argument('lower_price', type=float, help='Lower price bound')
    grid_parser.add_argument('upper_price', type=float, help='Upper price bound')
    grid_parser.add_argument('num_orders', type=int, help='Number of orders')
    grid_parser.add_argument('--grid-type', default='LINEAR', choices=['LINEAR', 'LOGARITHMIC'], help='Grid type')
    
    # DCA grid
    dca_parser = subparsers.add_parser('dca', help='Create DCA grid strategy')
    dca_parser.add_argument('symbol', help='Trading symbol')
    dca_parser.add_argument('side', choices=['BUY', 'SELL'], help='Order side')
    dca_parser.add_argument('total_quantity', type=float, help='Total quantity')
    dca_parser.add_argument('start_price', type=float, help='Starting price')
    dca_parser.add_argument('price_decrement', type=float, help='Price decrement')
    dca_parser.add_argument('num_orders', type=int, help='Number of orders')
    
    # Cancel order
    cancel_parser = subparsers.add_parser('cancel', help='Cancel order')
    cancel_parser.add_argument('symbol', help='Trading symbol')
    cancel_parser.add_argument('order_id', type=int, help='Order ID')
    
    # Order status
    status_parser = subparsers.add_parser('status', help='Get order status')
    status_parser.add_argument('symbol', help='Trading symbol')
    status_parser.add_argument('order_id', type=int, help='Order ID')
    
    # Account balance
    balance_parser = subparsers.add_parser('balance', help='Get account balance')
    
    # Configuration
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--set-api-key', help='Set API key')
    config_parser.add_argument('--set-api-secret', help='Set API secret')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.api_key:
        config['api_key'] = args.api_key
    if args.api_secret:
        config['api_secret'] = args.api_secret
    
    # Handle configuration commands
    if args.command == 'config':
        if args.set_api_key:
            config['api_key'] = args.set_api_key
            save_config(config, args.config)
            print(f"API key set: {args.set_api_key[:8]}...")
        elif args.set_api_secret:
            config['api_secret'] = args.set_api_secret
            save_config(config, args.config)
            print(f"API secret set: {args.set_api_secret[:8]}...")
        elif args.show:
            print("Current configuration:")
            for key, value in config.items():
                if 'secret' in key.lower() or 'key' in key.lower():
                    print(f"  {key}: {value[:8]}..." if value else f"  {key}: (not set)")
                else:
                    print(f"  {key}: {value}")
        return
    
    # Check for required API credentials
    if not config.get('api_key') or not config.get('api_secret'):
        print("Error: API key and secret are required.")
        print("Use 'python main.py config --set-api-key YOUR_KEY --set-api-secret YOUR_SECRET' to set them.")
        sys.exit(1)
    
    # Initialize bot
    testnet = args.testnet and not args.mainnet
    bot = BinanceTradingBot(
        api_key=config['api_key'],
        api_secret=config['api_secret'],
        testnet=testnet,
        log_file=args.log_file
    )
    
    try:
        # Execute commands
        if args.command == 'market':
            result = bot.market_order(args.symbol, args.side, args.quantity)
            print(f"Market order placed: {result}")
            
        elif args.command == 'limit':
            result = bot.limit_order(args.symbol, args.side, args.quantity, args.price, args.time_in_force)
            print(f"Limit order placed: {result}")
            
        elif args.command == 'stop-limit':
            result = bot.stop_limit_order(args.symbol, args.side, args.quantity, args.stop_price, args.limit_price, args.time_in_force)
            print(f"Stop-limit order placed: {result}")
            
        elif args.command == 'stop-market':
            result = bot.stop_market_order(args.symbol, args.side, args.quantity, args.stop_price)
            print(f"Stop-market order placed: {result}")
            
        elif args.command == 'take-profit':
            result = bot.take_profit_order(args.symbol, args.side, args.quantity, args.stop_price)
            print(f"Take-profit order placed: {result}")
            
        elif args.command == 'oco':
            result = bot.oco_order(args.symbol, args.side, args.quantity, args.take_profit_price, args.stop_loss_price, args.time_in_force)
            print(f"OCO order placed: {result}")
            
        elif args.command == 'twap':
            result = bot.twap_order(args.symbol, args.side, args.total_quantity, args.duration_minutes, args.num_slices, args.order_type, args.price)
            print(f"TWAP order started: {result}")
            
        elif args.command == 'grid':
            result = bot.grid_strategy(args.symbol, args.side, args.quantity_per_order, args.lower_price, args.upper_price, args.num_orders, args.grid_type)
            print(f"Grid strategy executed: {result}")
            
        elif args.command == 'dca':
            result = bot.dca_grid(args.symbol, args.side, args.total_quantity, args.start_price, args.price_decrement, args.num_orders)
            print(f"DCA grid executed: {result}")
            
        elif args.command == 'cancel':
            result = bot.cancel_order(args.symbol, args.order_id)
            print(f"Order canceled: {result}")
            
        elif args.command == 'status':
            result = bot.get_order_status(args.symbol, args.order_id)
            print(f"Order status: {result}")
            
        elif args.command == 'balance':
            result = bot.get_account_balance()
            print(f"Account balance: {result}")
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
