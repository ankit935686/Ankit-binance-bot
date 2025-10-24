from binance import Client
import logging
import time
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

class BasicBot:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True, log_file: str = 'bot.log'):
        """
        Initialize the Binance Futures trading bot.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet (True) or mainnet (False)
            log_file: Path to log file
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Initialize client
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            # Test connection
            self.client.futures_account()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Binance API: {e}")
        
        # Configure logging
        self._setup_logging(log_file)
        
        # Track active orders for OCO and advanced strategies
        self.active_orders = {}
        self.order_counter = 0

    def _setup_logging(self, log_file: str):
        """Setup logging configuration."""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else '.', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('BinanceBot')
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def validate_symbol(self, symbol: str) -> str:
        """Validate trading symbol format."""
        if not isinstance(symbol, str) or len(symbol) < 3:
            raise ValueError('Invalid symbol format')
        
        symbol = symbol.upper()
        
        # Check if symbol exists on Binance
        try:
            exchange_info = self.client.futures_exchange_info()
            valid_symbols = [s['symbol'] for s in exchange_info['symbols']]
            if symbol not in valid_symbols:
                raise ValueError(f'Symbol {symbol} not found on Binance Futures')
        except Exception as e:
            self.logger.warning(f"Could not validate symbol {symbol}: {e}")
            
        return symbol

    def validate_side(self, side: str) -> str:
        """Validate order side."""
        side = side.upper()
        if side not in ('BUY', 'SELL'):
            raise ValueError('Side must be BUY or SELL')
        return side

    def validate_quantity(self, quantity: float) -> float:
        """Validate order quantity."""
        try:
            q = float(quantity)
        except (ValueError, TypeError):
            raise ValueError('Quantity must be numeric')
        
        if q <= 0:
            raise ValueError('Quantity must be > 0')
            
        return q

    def validate_price(self, price: float) -> float:
        """Validate order price."""
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError('Price must be numeric')
        
        if p <= 0:
            raise ValueError('Price must be > 0')
            
        return p

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol trading rules and filters."""
        try:
            exchange_info = self.client.futures_exchange_info()
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return s
            raise ValueError(f'Symbol {symbol} not found')
        except Exception as e:
            self.logger.error(f"Error getting symbol info for {symbol}: {e}")
            raise

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Place a market order.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            
        Returns:
            Order response from Binance
        """
        symbol = self.validate_symbol(symbol)
        side = self.validate_side(side)
        quantity = self.validate_quantity(quantity)

        try:
            self.logger.info(f'Placing MARKET order: {symbol} {side} {quantity}')
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            self.logger.info(f'MARKET order placed successfully: {order}')
            return order
        except Exception as e:
            self.logger.error(f'Error placing MARKET order: {e}', exc_info=True)
            raise

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, 
                         time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Order price
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response from Binance
        """
        symbol = self.validate_symbol(symbol)
        side = self.validate_side(side)
        quantity = self.validate_quantity(quantity)
        price = self.validate_price(price)

        if time_in_force not in ['GTC', 'IOC', 'FOK']:
            raise ValueError('time_in_force must be GTC, IOC, or FOK')

        try:
            self.logger.info(f'Placing LIMIT order: {symbol} {side} {quantity} @ {price}')
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                price=str(price),
                quantity=quantity,
                timeInForce=time_in_force
            )
            self.logger.info(f'LIMIT order placed successfully: {order}')
            return order
        except Exception as e:
            self.logger.error(f'Error placing LIMIT order: {e}', exc_info=True)
            raise

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
            
        Returns:
            Cancellation response from Binance
        """
        try:
            self.logger.info(f'Canceling order: {symbol} {order_id}')
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            self.logger.info(f'Order canceled successfully: {result}')
            return result
        except Exception as e:
            self.logger.error(f'Error canceling order: {e}', exc_info=True)
            raise

    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order status.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            
        Returns:
            Order status from Binance
        """
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            return order
        except Exception as e:
            self.logger.error(f'Error getting order status: {e}', exc_info=True)
            raise

    def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance information."""
        try:
            balance = self.client.futures_account()
            return balance
        except Exception as e:
            self.logger.error(f'Error getting account balance: {e}', exc_info=True)
            raise
