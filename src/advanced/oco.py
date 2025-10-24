"""
OCO (One-Cancels-the-Other) Orders Implementation for Binance Futures Trading Bot

This module implements OCO orders which place two orders simultaneously:
- A take-profit order (limit order)
- A stop-loss order (stop order)

When one order is filled, the other is automatically canceled.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_bot import BasicBot


class OCOOrders:
    """Handle OCO (One-Cancels-the-Other) order operations."""
    
    def __init__(self, bot: BasicBot):
        """
        Initialize OCOOrders with a BasicBot instance.
        
        Args:
            bot: BasicBot instance for API operations
        """
        self.bot = bot
        self.logger = logging.getLogger('OCOOrders')
        self.active_oco_orders = {}
        self.monitoring_threads = {}
    
    def place_oco_order(self, symbol: str, side: str, quantity: float,
                       take_profit_price: float, stop_loss_price: float,
                       time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place an OCO order (take-profit + stop-loss).
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            take_profit_price: Price for take-profit limit order
            stop_loss_price: Price for stop-loss order
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Dictionary containing both order responses
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        quantity = self.bot.validate_quantity(quantity)
        take_profit_price = self.bot.validate_price(take_profit_price)
        stop_loss_price = self.bot.validate_price(stop_loss_price)
        
        if time_in_force not in ['GTC', 'IOC', 'FOK']:
            raise ValueError('time_in_force must be GTC, IOC, or FOK')
        
        # Validate OCO logic
        if side == 'BUY':
            if take_profit_price <= stop_loss_price:
                raise ValueError('For BUY orders: take_profit_price must be > stop_loss_price')
        else:  # SELL
            if take_profit_price >= stop_loss_price:
                raise ValueError('For SELL orders: take_profit_price must be < stop_loss_price')
        
        try:
            self.logger.info(f'Placing OCO order: {symbol} {side} {quantity} TP@{take_profit_price} SL@{stop_loss_price}')
            
            # Place take-profit limit order
            take_profit_order = self.bot.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=str(take_profit_price),
                timeInForce=time_in_force
            )
            
            # Place stop-loss order
            stop_loss_order = self.bot.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=str(stop_loss_price)
            )
            
            # Store OCO order pair
            oco_id = f"{symbol}_{int(time.time())}"
            self.active_oco_orders[oco_id] = {
                'symbol': symbol,
                'side': side,
                'take_profit_order': take_profit_order,
                'stop_loss_order': stop_loss_order,
                'status': 'ACTIVE'
            }
            
            # Start monitoring thread
            self._start_oco_monitoring(oco_id)
            
            result = {
                'oco_id': oco_id,
                'take_profit_order': take_profit_order,
                'stop_loss_order': stop_loss_order,
                'status': 'PLACED'
            }
            
            self.logger.info(f'OCO order placed successfully: {result}')
            return result
            
        except Exception as e:
            self.logger.error(f'Error placing OCO order: {e}', exc_info=True)
            raise
    
    def _start_oco_monitoring(self, oco_id: str):
        """Start monitoring thread for OCO order."""
        def monitor_oco():
            while oco_id in self.active_oco_orders:
                try:
                    oco_data = self.active_oco_orders[oco_id]
                    symbol = oco_data['symbol']
                    
                    # Check take-profit order status
                    tp_order_id = oco_data['take_profit_order']['orderId']
                    tp_status = self.bot.get_order_status(symbol, tp_order_id)
                    
                    # Check stop-loss order status
                    sl_order_id = oco_data['stop_loss_order']['orderId']
                    sl_status = self.bot.get_order_status(symbol, sl_order_id)
                    
                    # If either order is filled, cancel the other
                    if tp_status['status'] == 'FILLED':
                        self.logger.info(f'Take-profit filled for OCO {oco_id}, canceling stop-loss')
                        try:
                            self.bot.cancel_order(symbol, sl_order_id)
                        except Exception as e:
                            self.logger.warning(f'Could not cancel stop-loss: {e}')
                        self.active_oco_orders[oco_id]['status'] = 'TAKE_PROFIT_FILLED'
                        break
                    
                    elif sl_status['status'] == 'FILLED':
                        self.logger.info(f'Stop-loss filled for OCO {oco_id}, canceling take-profit')
                        try:
                            self.bot.cancel_order(symbol, tp_order_id)
                        except Exception as e:
                            self.logger.warning(f'Could not cancel take-profit: {e}')
                        self.active_oco_orders[oco_id]['status'] = 'STOP_LOSS_FILLED'
                        break
                    
                    # If both orders are canceled or expired, stop monitoring
                    elif (tp_status['status'] in ['CANCELED', 'EXPIRED'] and 
                          sl_status['status'] in ['CANCELED', 'EXPIRED']):
                        self.logger.info(f'Both orders canceled/expired for OCO {oco_id}')
                        self.active_oco_orders[oco_id]['status'] = 'CANCELED'
                        break
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    self.logger.error(f'Error monitoring OCO {oco_id}: {e}')
                    time.sleep(5)  # Wait longer on error
            
            # Clean up
            if oco_id in self.active_oco_orders:
                del self.active_oco_orders[oco_id]
            if oco_id in self.monitoring_threads:
                del self.monitoring_threads[oco_id]
        
        thread = threading.Thread(target=monitor_oco, daemon=True)
        thread.start()
        self.monitoring_threads[oco_id] = thread
    
    def cancel_oco_order(self, oco_id: str) -> Dict[str, Any]:
        """
        Cancel an OCO order (both take-profit and stop-loss).
        
        Args:
            oco_id: OCO order ID
            
        Returns:
            Cancellation results
        """
        if oco_id not in self.active_oco_orders:
            raise ValueError(f'OCO order {oco_id} not found')
        
        oco_data = self.active_oco_orders[oco_id]
        symbol = oco_data['symbol']
        
        results = {'oco_id': oco_id, 'cancellations': []}
        
        try:
            # Cancel take-profit order
            tp_order_id = oco_data['take_profit_order']['orderId']
            try:
                tp_result = self.bot.cancel_order(symbol, tp_order_id)
                results['cancellations'].append({'order': 'take_profit', 'result': tp_result})
            except Exception as e:
                self.logger.warning(f'Could not cancel take-profit: {e}')
                results['cancellations'].append({'order': 'take_profit', 'error': str(e)})
            
            # Cancel stop-loss order
            sl_order_id = oco_data['stop_loss_order']['orderId']
            try:
                sl_result = self.bot.cancel_order(symbol, sl_order_id)
                results['cancellations'].append({'order': 'stop_loss', 'result': sl_result})
            except Exception as e:
                self.logger.warning(f'Could not cancel stop-loss: {e}')
                results['cancellations'].append({'order': 'stop_loss', 'error': str(e)})
            
            # Mark as canceled
            self.active_oco_orders[oco_id]['status'] = 'CANCELED'
            
            self.logger.info(f'OCO order {oco_id} canceled: {results}')
            return results
            
        except Exception as e:
            self.logger.error(f'Error canceling OCO order {oco_id}: {e}', exc_info=True)
            raise
    
    def get_oco_status(self, oco_id: str) -> Dict[str, Any]:
        """
        Get status of an OCO order.
        
        Args:
            oco_id: OCO order ID
            
        Returns:
            OCO order status
        """
        if oco_id not in self.active_oco_orders:
            raise ValueError(f'OCO order {oco_id} not found')
        
        return self.active_oco_orders[oco_id]
    
    def get_all_oco_orders(self) -> Dict[str, Any]:
        """Get all active OCO orders."""
        return self.active_oco_orders
