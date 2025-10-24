"""
Grid Orders Strategy Implementation for Binance Futures Trading Bot

This module implements grid trading strategy which places multiple buy and sell orders
at regular price intervals to profit from market volatility within a price range.
"""

import time
import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_bot import BasicBot


class GridOrders:
    """Handle Grid Orders strategy operations."""
    
    def __init__(self, bot: BasicBot):
        """
        Initialize GridOrders with a BasicBot instance.
        
        Args:
            bot: BasicBot instance for API operations
        """
        self.bot = bot
        self.logger = logging.getLogger('GridOrders')
        self.active_grids = {}
    
    def create_grid_strategy(self, symbol: str, side: str, quantity_per_order: float,
                            lower_price: float, upper_price: float, num_orders: int,
                            grid_type: str = 'LINEAR', price_step: float = None) -> Dict[str, Any]:
        """
        Create a grid trading strategy.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            side: Primary side ('BUY' or 'SELL')
            quantity_per_order: Quantity for each grid order
            lower_price: Lower bound of the grid
            upper_price: Upper bound of the grid
            num_orders: Number of orders in the grid
            grid_type: Type of grid ('LINEAR' or 'LOGARITHMIC')
            price_step: Fixed price step (if None, calculated automatically)
            
        Returns:
            Grid strategy configuration
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        quantity_per_order = self.bot.validate_quantity(quantity_per_order)
        lower_price = self.bot.validate_price(lower_price)
        upper_price = self.bot.validate_price(upper_price)
        
        if lower_price >= upper_price:
            raise ValueError('lower_price must be < upper_price')
        
        if num_orders <= 0:
            raise ValueError('num_orders must be > 0')
        
        if grid_type not in ['LINEAR', 'LOGARITHMIC']:
            raise ValueError('grid_type must be LINEAR or LOGARITHMIC')
        
        # Calculate price levels
        if price_step is None:
            if grid_type == 'LINEAR':
                price_step = (upper_price - lower_price) / (num_orders - 1)
            else:  # LOGARITHMIC
                price_step = (math.log(upper_price) - math.log(lower_price)) / (num_orders - 1)
        else:
            price_step = self.bot.validate_price(price_step)
        
        # Generate grid levels
        grid_levels = []
        for i in range(num_orders):
            if grid_type == 'LINEAR':
                price = lower_price + (i * price_step)
            else:  # LOGARITHMIC
                price = lower_price * math.exp(i * price_step)
            
            # Determine order side for this level
            # For BUY grid: lower prices are BUY, higher prices are SELL
            # For SELL grid: lower prices are BUY, higher prices are SELL
            if side == 'BUY':
                order_side = 'BUY' if i < num_orders // 2 else 'SELL'
            else:
                order_side = 'SELL' if i < num_orders // 2 else 'BUY'
            
            grid_levels.append({
                'level': i + 1,
                'price': round(price, 8),
                'side': order_side,
                'quantity': quantity_per_order
            })
        
        # Generate grid ID
        grid_id = f"GRID_{symbol}_{int(time.time())}"
        
        # Store grid configuration
        self.active_grids[grid_id] = {
            'symbol': symbol,
            'side': side,
            'quantity_per_order': quantity_per_order,
            'lower_price': lower_price,
            'upper_price': upper_price,
            'num_orders': num_orders,
            'grid_type': grid_type,
            'price_step': price_step,
            'grid_levels': grid_levels,
            'status': 'CONFIGURED',
            'placed_orders': [],
            'filled_orders': [],
            'created_time': datetime.now()
        }
        
        self.logger.info(f'Grid strategy created: {grid_id} - {symbol} {side} {num_orders} orders between {lower_price}-{upper_price}')
        
        return {
            'grid_id': grid_id,
            'symbol': symbol,
            'side': side,
            'num_orders': num_orders,
            'grid_levels': grid_levels,
            'status': 'CONFIGURED'
        }
    
    def execute_grid_orders(self, grid_id: str) -> Dict[str, Any]:
        """
        Execute all orders in the grid strategy.
        
        Args:
            grid_id: Grid strategy ID
            
        Returns:
            Execution results
        """
        if grid_id not in self.active_grids:
            raise ValueError(f'Grid {grid_id} not found')
        
        grid_data = self.active_grids[grid_id]
        grid_data['status'] = 'EXECUTING'
        
        placed_orders = []
        failed_orders = []
        
        try:
            for level in grid_data['grid_levels']:
                try:
                    # Place limit order for this grid level
                    order = self.bot.place_limit_order(
                        symbol=grid_data['symbol'],
                        side=level['side'],
                        quantity=level['quantity'],
                        price=level['price']
                    )
                    
                    # Store order info with grid level
                    order_info = {
                        'grid_level': level['level'],
                        'price': level['price'],
                        'side': level['side'],
                        'quantity': level['quantity'],
                        'order': order,
                        'timestamp': datetime.now()
                    }
                    
                    placed_orders.append(order_info)
                    grid_data['placed_orders'].append(order_info)
                    
                    self.logger.info(f'Grid {grid_id} level {level["level"]} order placed: {level["side"]} {level["quantity"]} @ {level["price"]}')
                    
                    # Small delay between orders to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f'Grid {grid_id} level {level["level"]} failed: {e}')
                    failed_orders.append({
                        'grid_level': level['level'],
                        'price': level['price'],
                        'side': level['side'],
                        'quantity': level['quantity'],
                        'error': str(e),
                        'timestamp': datetime.now()
                    })
            
            grid_data['status'] = 'ACTIVE'
            
            self.logger.info(f'Grid {grid_id} execution completed. Placed: {len(placed_orders)}, Failed: {len(failed_orders)}')
            
            return {
                'grid_id': grid_id,
                'status': 'ACTIVE',
                'placed_orders': len(placed_orders),
                'failed_orders': len(failed_orders),
                'orders': placed_orders
            }
            
        except Exception as e:
            grid_data['status'] = 'ERROR'
            self.logger.error(f'Grid {grid_id} execution failed: {e}', exc_info=True)
            raise
    
    def cancel_grid_orders(self, grid_id: str) -> Dict[str, Any]:
        """
        Cancel all orders in the grid strategy.
        
        Args:
            grid_id: Grid strategy ID
            
        Returns:
            Cancellation results
        """
        if grid_id not in self.active_grids:
            raise ValueError(f'Grid {grid_id} not found')
        
        grid_data = self.active_grids[grid_id]
        symbol = grid_data['symbol']
        
        canceled_orders = []
        failed_cancellations = []
        
        try:
            for order_info in grid_data['placed_orders']:
                try:
                    order_id = order_info['order']['orderId']
                    cancel_result = self.bot.cancel_order(symbol, order_id)
                    
                    canceled_orders.append({
                        'grid_level': order_info['grid_level'],
                        'order_id': order_id,
                        'result': cancel_result
                    })
                    
                    self.logger.info(f'Grid {grid_id} level {order_info["grid_level"]} order canceled')
                    
                except Exception as e:
                    self.logger.warning(f'Could not cancel grid {grid_id} level {order_info["grid_level"]}: {e}')
                    failed_cancellations.append({
                        'grid_level': order_info['grid_level'],
                        'order_id': order_info['order']['orderId'],
                        'error': str(e)
                    })
            
            grid_data['status'] = 'CANCELED'
            
            self.logger.info(f'Grid {grid_id} cancellation completed. Canceled: {len(canceled_orders)}, Failed: {len(failed_cancellations)}')
            
            return {
                'grid_id': grid_id,
                'status': 'CANCELED',
                'canceled_orders': len(canceled_orders),
                'failed_cancellations': len(failed_cancellations),
                'results': canceled_orders
            }
            
        except Exception as e:
            self.logger.error(f'Grid {grid_id} cancellation failed: {e}', exc_info=True)
            raise
    
    def get_grid_status(self, grid_id: str) -> Dict[str, Any]:
        """
        Get status of a grid strategy.
        
        Args:
            grid_id: Grid strategy ID
            
        Returns:
            Grid strategy status
        """
        if grid_id not in self.active_grids:
            raise ValueError(f'Grid {grid_id} not found')
        
        grid_data = self.active_grids[grid_id]
        
        # Check order statuses
        active_orders = 0
        filled_orders = 0
        canceled_orders = 0
        
        for order_info in grid_data['placed_orders']:
            try:
                order_status = self.bot.get_order_status(grid_data['symbol'], order_info['order']['orderId'])
                if order_status['status'] == 'FILLED':
                    filled_orders += 1
                    if order_info not in grid_data['filled_orders']:
                        grid_data['filled_orders'].append(order_info)
                elif order_status['status'] in ['CANCELED', 'EXPIRED']:
                    canceled_orders += 1
                else:
                    active_orders += 1
            except Exception as e:
                self.logger.warning(f'Could not check order status for grid {grid_id}: {e}')
        
        return {
            'grid_id': grid_id,
            'symbol': grid_data['symbol'],
            'side': grid_data['side'],
            'status': grid_data['status'],
            'num_orders': grid_data['num_orders'],
            'active_orders': active_orders,
            'filled_orders': filled_orders,
            'canceled_orders': canceled_orders,
            'created_time': grid_data['created_time'],
            'grid_levels': grid_data['grid_levels']
        }
    
    def get_all_grids(self) -> Dict[str, Any]:
        """Get all grid strategies."""
        return self.active_grids
    
    def create_dca_grid(self, symbol: str, side: str, total_quantity: float,
                       start_price: float, price_decrement: float, num_orders: int) -> Dict[str, Any]:
        """
        Create a Dollar Cost Averaging (DCA) grid strategy.
        
        Args:
            symbol: Trading symbol
            side: Order side
            total_quantity: Total quantity to distribute
            start_price: Starting price
            price_decrement: Price decrement for each level
            num_orders: Number of orders
            
        Returns:
            DCA grid configuration
        """
        symbol = self.bot.validate_symbol(symbol)
        side = self.bot.validate_side(side)
        total_quantity = self.bot.validate_quantity(total_quantity)
        start_price = self.bot.validate_price(start_price)
        price_decrement = self.bot.validate_price(price_decrement)
        
        if num_orders <= 0:
            raise ValueError('num_orders must be > 0')
        
        # Calculate quantity per order
        quantity_per_order = total_quantity / num_orders
        
        # Calculate price levels
        lower_price = start_price - (num_orders - 1) * price_decrement
        upper_price = start_price
        
        if lower_price <= 0:
            raise ValueError('Calculated lower_price is <= 0')
        
        self.logger.info(f'Creating DCA grid: {symbol} {side} {total_quantity} from {start_price} down to {lower_price}')
        
        return self.create_grid_strategy(
            symbol=symbol,
            side=side,
            quantity_per_order=quantity_per_order,
            lower_price=lower_price,
            upper_price=upper_price,
            num_orders=num_orders,
            grid_type='LINEAR',
            price_step=price_decrement
        )
