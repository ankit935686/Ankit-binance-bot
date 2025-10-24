"""
Stop-Limit Orders Implementation for Binance Futures Trading Bot

This module implements stop-limit orders which combine stop orders with limit orders.
A stop-limit order becomes a limit order when the stop price is reached.
"""

import time
import logging
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_bot import BasicBot


class StopLimitOrders:
    """Handle stop-limit order operations."""
    
    def __init__(self, bot: BasicBot):
        """
        Initialize StopLimitOrders with a BasicBot instance.
        
        Args:
            bot: BasicBot instance for API operations
        """
        self.bot = bot
        self.logger = logging.getLogger('StopLimitOrders')
    
    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, 
                              stop_price: float, limit_price: float, 
                              time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a stop-limit order.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            stop_price: Price that triggers the order
            limit_price: Price for the limit order when triggered
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response from Binance
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        quantity = self.bot.validate_quantity(quantity)
        stop_price = self.bot.validate_price(stop_price)
        limit_price = self.bot.validate_price(limit_price)
        
        if time_in_force not in ['GTC', 'IOC', 'FOK']:
            raise ValueError('time_in_force must be GTC, IOC, or FOK')
        
        # Validate stop-limit logic
        if side == 'BUY' and stop_price <= limit_price:
            raise ValueError('For BUY orders: stop_price must be > limit_price')
        elif side == 'SELL' and stop_price >= limit_price:
            raise ValueError('For SELL orders: stop_price must be < limit_price')
        
        try:
            self.logger.info(f'Placing STOP_LIMIT order: {symbol} {side} {quantity} stop@{stop_price} limit@{limit_price}')
            
            order = self.bot.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=quantity,
                stopPrice=str(stop_price),
                price=str(limit_price),
                timeInForce=time_in_force
            )
            
            self.logger.info(f'STOP_LIMIT order placed successfully: {order}')
            return order
            
        except Exception as e:
            self.logger.error(f'Error placing STOP_LIMIT order: {e}', exc_info=True)
            raise
    
    def place_stop_market_order(self, symbol: str, side: str, quantity: float, 
                               stop_price: float) -> Dict[str, Any]:
        """
        Place a stop-market order (stop-loss order).
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            stop_price: Price that triggers the market order
            
        Returns:
            Order response from Binance
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        quantity = self.bot.validate_quantity(quantity)
        stop_price = self.bot.validate_price(stop_price)
        
        try:
            self.logger.info(f'Placing STOP_MARKET order: {symbol} {side} {quantity} stop@{stop_price}')
            
            order = self.bot.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=str(stop_price)
            )
            
            self.logger.info(f'STOP_MARKET order placed successfully: {order}')
            return order
            
        except Exception as e:
            self.logger.error(f'Error placing STOP_MARKET order: {e}', exc_info=True)
            raise
    
    def place_take_profit_order(self, symbol: str, side: str, quantity: float, 
                               stop_price: float) -> Dict[str, Any]:
        """
        Place a take-profit order.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            stop_price: Price that triggers the take-profit
            
        Returns:
            Order response from Binance
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        quantity = self.bot.validate_quantity(quantity)
        stop_price = self.bot.validate_price(stop_price)
        
        try:
            self.logger.info(f'Placing TAKE_PROFIT order: {symbol} {side} {quantity} stop@{stop_price}')
            
            order = self.bot.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='TAKE_PROFIT',
                quantity=quantity,
                stopPrice=str(stop_price)
            )
            
            self.logger.info(f'TAKE_PROFIT order placed successfully: {order}')
            return order
            
        except Exception as e:
            self.logger.error(f'Error placing TAKE_PROFIT order: {e}', exc_info=True)
            raise
    
    def place_take_profit_limit_order(self, symbol: str, side: str, quantity: float, 
                                     stop_price: float, limit_price: float,
                                     time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a take-profit limit order.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            stop_price: Price that triggers the order
            limit_price: Price for the limit order when triggered
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response from Binance
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        quantity = self.bot.validate_quantity(quantity)
        stop_price = self.bot.validate_price(stop_price)
        limit_price = self.bot.validate_price(limit_price)
        
        if time_in_force not in ['GTC', 'IOC', 'FOK']:
            raise ValueError('time_in_force must be GTC, IOC, or FOK')
        
        # Validate take-profit logic
        if side == 'BUY' and stop_price >= limit_price:
            raise ValueError('For BUY orders: stop_price must be < limit_price')
        elif side == 'SELL' and stop_price <= limit_price:
            raise ValueError('For SELL orders: stop_price must be > limit_price')
        
        try:
            self.logger.info(f'Placing TAKE_PROFIT_LIMIT order: {symbol} {side} {quantity} stop@{stop_price} limit@{limit_price}')
            
            order = self.bot.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='TAKE_PROFIT_LIMIT',
                quantity=quantity,
                stopPrice=str(stop_price),
                price=str(limit_price),
                timeInForce=time_in_force
            )
            
            self.logger.info(f'TAKE_PROFIT_LIMIT order placed successfully: {order}')
            return order
            
        except Exception as e:
            self.logger.error(f'Error placing TAKE_PROFIT_LIMIT order: {e}', exc_info=True)
            raise
