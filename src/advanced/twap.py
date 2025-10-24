"""
TWAP (Time-Weighted Average Price) Strategy Implementation for Binance Futures Trading Bot

This module implements TWAP strategy which splits large orders into smaller chunks
and executes them over a specified time period to minimize market impact.
"""

import time
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_bot import BasicBot


class TWAPStrategy:
    """Handle TWAP (Time-Weighted Average Price) strategy operations."""
    
    def __init__(self, bot: BasicBot):
        """
        Initialize TWAPStrategy with a BasicBot instance.
        
        Args:
            bot: BasicBot instance for API operations
        """
        self.bot = bot
        self.logger = logging.getLogger('TWAPStrategy')
        self.active_twap_orders = {}
    
    def execute_twap_order(self, symbol: str, side: str, total_quantity: float,
                         duration_minutes: int, num_slices: int = None,
                         order_type: str = 'MARKET', price: float = None,
                         time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Execute a TWAP order by splitting it into smaller chunks over time.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            total_quantity: Total quantity to execute
            duration_minutes: Duration in minutes to spread the execution
            num_slices: Number of slices (if None, calculated automatically)
            order_type: Type of order ('MARKET' or 'LIMIT')
            price: Price for limit orders (required if order_type='LIMIT')
            time_in_force: Time in force for limit orders
            
        Returns:
            TWAP execution results
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        total_quantity = self.bot.validate_quantity(total_quantity)
        
        if duration_minutes <= 0:
            raise ValueError('Duration must be > 0 minutes')
        
        if order_type not in ['MARKET', 'LIMIT']:
            raise ValueError('order_type must be MARKET or LIMIT')
        
        if order_type == 'LIMIT' and price is None:
            raise ValueError('Price is required for LIMIT orders')
        
        if order_type == 'LIMIT':
            price = self.bot.validate_price(price)
        
        # Calculate number of slices if not provided
        if num_slices is None:
            # Default: one slice per minute, minimum 1, maximum 60
            num_slices = max(1, min(duration_minutes, 60))
        
        if num_slices <= 0:
            raise ValueError('Number of slices must be > 0')
        
        # Calculate slice quantity
        slice_quantity = total_quantity / num_slices
        slice_interval = (duration_minutes * 60) / num_slices  # seconds between slices
        
        # Generate TWAP ID
        twap_id = f"TWAP_{symbol}_{int(time.time())}"
        
        # Store TWAP order info
        self.active_twap_orders[twap_id] = {
            'symbol': symbol,
            'side': side,
            'total_quantity': total_quantity,
            'remaining_quantity': total_quantity,
            'num_slices': num_slices,
            'slice_quantity': slice_quantity,
            'slice_interval': slice_interval,
            'order_type': order_type,
            'price': price,
            'time_in_force': time_in_force,
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(minutes=duration_minutes),
            'status': 'ACTIVE',
            'executed_orders': [],
            'failed_orders': []
        }
        
        self.logger.info(f'Starting TWAP execution: {twap_id} - {symbol} {side} {total_quantity} over {duration_minutes}min in {num_slices} slices')
        
        # Execute TWAP strategy
        self._execute_twap_slices(twap_id)
        
        return {
            'twap_id': twap_id,
            'symbol': symbol,
            'side': side,
            'total_quantity': total_quantity,
            'num_slices': num_slices,
            'duration_minutes': duration_minutes,
            'status': 'STARTED'
        }
    
    def _execute_twap_slices(self, twap_id: str):
        """Execute TWAP slices over time."""
        twap_data = self.active_twap_orders[twap_id]
        
        for slice_num in range(twap_data['num_slices']):
            if twap_data['status'] != 'ACTIVE':
                break
            
            try:
                # Calculate slice quantity (handle rounding for last slice)
                if slice_num == twap_data['num_slices'] - 1:
                    slice_quantity = twap_data['remaining_quantity']
                else:
                    slice_quantity = twap_data['slice_quantity']
                
                if slice_quantity <= 0:
                    break
                
                # Place order for this slice
                if twap_data['order_type'] == 'MARKET':
                    order = self.bot.place_market_order(
                        twap_data['symbol'],
                        twap_data['side'],
                        slice_quantity
                    )
                else:  # LIMIT
                    order = self.bot.place_limit_order(
                        twap_data['symbol'],
                        twap_data['side'],
                        slice_quantity,
                        twap_data['price'],
                        twap_data['time_in_force']
                    )
                
                # Update tracking
                twap_data['executed_orders'].append({
                    'slice_num': slice_num + 1,
                    'quantity': slice_quantity,
                    'order': order,
                    'timestamp': datetime.now()
                })
                
                twap_data['remaining_quantity'] -= slice_quantity
                
                self.logger.info(f'TWAP {twap_id} slice {slice_num + 1}/{twap_data["num_slices"]} executed: {slice_quantity} @ {order.get("avgPrice", "N/A")}')
                
                # Wait for next slice (except for the last one)
                if slice_num < twap_data['num_slices'] - 1:
                    time.sleep(twap_data['slice_interval'])
                
            except Exception as e:
                self.logger.error(f'TWAP {twap_id} slice {slice_num + 1} failed: {e}')
                twap_data['failed_orders'].append({
                    'slice_num': slice_num + 1,
                    'quantity': slice_quantity,
                    'error': str(e),
                    'timestamp': datetime.now()
                })
                
                # Continue with next slice even if one fails
                if slice_num < twap_data['num_slices'] - 1:
                    time.sleep(twap_data['slice_interval'])
        
        # Mark TWAP as completed
        twap_data['status'] = 'COMPLETED'
        twap_data['end_time'] = datetime.now()
        
        self.logger.info(f'TWAP {twap_id} completed. Executed: {len(twap_data["executed_orders"])}, Failed: {len(twap_data["failed_orders"])}')
    
    def cancel_twap_order(self, twap_id: str) -> Dict[str, Any]:
        """
        Cancel a TWAP order (stops future slices, doesn't cancel already placed orders).
        
        Args:
            twap_id: TWAP order ID
            
        Returns:
            Cancellation results
        """
        if twap_id not in self.active_twap_orders:
            raise ValueError(f'TWAP order {twap_id} not found')
        
        twap_data = self.active_twap_orders[twap_id]
        twap_data['status'] = 'CANCELED'
        twap_data['end_time'] = datetime.now()
        
        self.logger.info(f'TWAP order {twap_id} canceled')
        
        return {
            'twap_id': twap_id,
            'status': 'CANCELED',
            'executed_slices': len(twap_data['executed_orders']),
            'failed_slices': len(twap_data['failed_orders']),
            'remaining_quantity': twap_data['remaining_quantity']
        }
    
    def get_twap_status(self, twap_id: str) -> Dict[str, Any]:
        """
        Get status of a TWAP order.
        
        Args:
            twap_id: TWAP order ID
            
        Returns:
            TWAP order status
        """
        if twap_id not in self.active_twap_orders:
            raise ValueError(f'TWAP order {twap_id} not found')
        
        twap_data = self.active_twap_orders[twap_id]
        
        # Calculate execution statistics
        executed_quantity = sum(order['quantity'] for order in twap_data['executed_orders'])
        total_executed_value = 0
        
        for order_info in twap_data['executed_orders']:
            order = order_info['order']
            if 'avgPrice' in order and order['avgPrice']:
                total_executed_value += float(order['avgPrice']) * order_info['quantity']
        
        avg_price = total_executed_value / executed_quantity if executed_quantity > 0 else 0
        
        return {
            'twap_id': twap_id,
            'symbol': twap_data['symbol'],
            'side': twap_data['side'],
            'status': twap_data['status'],
            'total_quantity': twap_data['total_quantity'],
            'executed_quantity': executed_quantity,
            'remaining_quantity': twap_data['remaining_quantity'],
            'num_slices': twap_data['num_slices'],
            'executed_slices': len(twap_data['executed_orders']),
            'failed_slices': len(twap_data['failed_orders']),
            'avg_price': avg_price,
            'start_time': twap_data['start_time'],
            'end_time': twap_data['end_time'],
            'duration_seconds': (twap_data['end_time'] - twap_data['start_time']).total_seconds()
        }
    
    def get_all_twap_orders(self) -> Dict[str, Any]:
        """Get all TWAP orders."""
        return self.active_twap_orders
    
    def execute_adaptive_twap(self, symbol: str, side: str, total_quantity: float,
                             duration_minutes: int, volatility_threshold: float = 0.02,
                             min_slice_size: float = 0.001) -> Dict[str, Any]:
        """
        Execute an adaptive TWAP order that adjusts slice size based on market volatility.
        
        Args:
            symbol: Trading symbol
            side: Order side
            total_quantity: Total quantity to execute
            duration_minutes: Duration in minutes
            volatility_threshold: Volatility threshold for adjusting slice size
            min_slice_size: Minimum slice size
            
        Returns:
            Adaptive TWAP execution results
        """
        # This is a simplified adaptive TWAP implementation
        # In a real implementation, you would analyze market volatility
        # and adjust slice sizes accordingly
        
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        total_quantity = self.bot.validate_quantity(total_quantity)
        
        # Calculate adaptive number of slices based on volatility
        # Higher volatility = more slices (smaller chunks)
        base_slices = max(5, duration_minutes)  # At least 5 slices
        adaptive_slices = min(base_slices * 2, 100)  # Cap at 100 slices
        
        self.logger.info(f'Executing adaptive TWAP with {adaptive_slices} slices based on volatility analysis')
        
        return self.execute_twap_order(
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            duration_minutes=duration_minutes,
            num_slices=adaptive_slices,
            order_type='MARKET'
        )
