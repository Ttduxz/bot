#!/usr/bin/env python3
"""
Unified API Manager for XAU/USD Scalping Bot
Handles MT5 API with mock fallback for non-Windows systems
"""

import platform
import logging
from typing import Optional, Dict, Any, List
from config import CONFIG

# Initialize logger
logger = logging.getLogger(__name__)

# Global API instance
_api_instance = None
_api_type = None

def initialize_mt5_api() -> bool:
    """
    Initialize MT5 API connection
    Returns True if successful, False otherwise
    """
    global _api_instance, _api_type
    
    try:
        # Try to import MT5
        import MetaTrader5 as mt5
        
        # Initialize MT5
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        
        # Login to MT5
        login = CONFIG['mt5_login']
        password = CONFIG['mt5_password']
        server = CONFIG['mt5_server']
        
        if not mt5.login(login=login, password=password, server=server):
            logger.error(f"MT5 login failed: {mt5.last_error()}")
            return False
        
        _api_instance = mt5
        _api_type = 'mt5'
        logger.info("MT5 API initialized successfully")
        return True
        
    except ImportError:
        logger.warning("MetaTrader5 package not available")
        return False
    except Exception as e:
        logger.error(f"Error initializing MT5 API: {str(e)}")
        return False

def initialize_mock_api() -> bool:
    """
    Initialize mock API for testing/development
    Returns True if successful, False otherwise
    """
    global _api_instance, _api_type
    
    try:
        from mock_mt5 import MockMT5
        _api_instance = MockMT5()
        _api_type = 'mock'
        logger.info("Mock API initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing mock API: {str(e)}")
        return False

def initialize_api() -> bool:
    """
    Initialize the best available API
    Returns True if successful, False otherwise
    """
    # Try MT5 first (Windows)
    if platform.system() == 'Windows':
        if initialize_mt5_api():
            return True
    
    # Fallback to mock API
    logger.info("Falling back to mock API")
    return initialize_mock_api()

def get_api_type() -> str:
    """Get the current API type"""
    return _api_type or 'none'

def is_api_connected() -> bool:
    """Check if API is connected"""
    return _api_instance is not None

# MT5 API Functions
def account_info() -> Optional[Dict[str, Any]]:
    """Get account information"""
    if not _api_instance:
        return None
    
    try:
        if _api_type == 'mt5':
            account = _api_instance.account_info()
            if account:
                return {
                    'login': account.login,
                    'balance': account.balance,
                    'equity': account.equity,
                    'margin': account.margin,
                    'profit': account.profit
                }
        elif _api_type == 'mock':
            return _api_instance.account_info()
    except Exception as e:
        logger.error(f"Error getting account info: {str(e)}")
    
    return None

def symbol_info(symbol: str) -> Optional[Any]:
    """Get symbol information"""
    if not _api_instance:
        return None
    
    try:
        if _api_type == 'mt5':
            return _api_instance.symbol_info(symbol)
        elif _api_type == 'mock':
            return _api_instance.symbol_info(symbol)
    except Exception as e:
        logger.error(f"Error getting symbol info: {str(e)}")
    
    return None

def copy_rates_from(symbol: str, timeframe: str, start_pos: int, count: int) -> Optional[List]:
    """Get historical data"""
    if not _api_instance:
        return None
    
    try:
        if _api_type == 'mt5':
            # Convert timeframe string to MT5 constant
            tf_map = {
                'M1': _api_instance.TIMEFRAME_M1,
                'M5': _api_instance.TIMEFRAME_M5,
                'M15': _api_instance.TIMEFRAME_M15,
                'M30': _api_instance.TIMEFRAME_M30,
                'H1': _api_instance.TIMEFRAME_H1,
                'H4': _api_instance.TIMEFRAME_H4,
                'D1': _api_instance.TIMEFRAME_D1
            }
            mt5_timeframe = tf_map.get(timeframe, _api_instance.TIMEFRAME_M1)
            
            rates = _api_instance.copy_rates_from_pos(symbol, mt5_timeframe, start_pos, count)
            return rates.tolist() if rates is not None else None
            
        elif _api_type == 'mock':
            return _api_instance.copy_rates_from(symbol, timeframe, start_pos, count)
    except Exception as e:
        logger.error(f"Error getting historical data: {str(e)}")
    
    return None

def order_send(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send order"""
    if not _api_instance:
        return None
    
    try:
        if _api_type == 'mt5':
            # Convert request to MT5 format
            action = _api_instance.TRADE_ACTION_DEAL
            symbol = request['symbol']
            volume = request['volume']
            order_type = _api_instance.ORDER_TYPE_BUY if request['order_type'] == 'BUY' else _api_instance.ORDER_TYPE_SELL
            price = request.get('price')
            sl = request.get('sl')
            tp = request.get('tp')
            comment = request.get('comment', 'Bot order')
            
            result = _api_instance.order_send({
                'action': action,
                'symbol': symbol,
                'volume': volume,
                'type': order_type,
                'price': price,
                'sl': sl,
                'tp': tp,
                'comment': comment,
                'type_time': _api_instance.ORDER_TIME_GTC,
                'type_filling': _api_instance.ORDER_FILLING_IOC
            })
            
            if result.retcode == _api_instance.TRADE_RETCODE_DONE:
                return {
                    'order': result.order,
                    'volume': result.volume,
                    'price': result.price,
                    'retcode': result.retcode,
                    'comment': result.comment
                }
            else:
                logger.error(f"Order failed: {result.comment}")
                return None
                
        elif _api_type == 'mock':
            return _api_instance.order_send(request)
    except Exception as e:
        logger.error(f"Error sending order: {str(e)}")
    
    return None

def positions_get(symbol: str = None) -> List[Dict[str, Any]]:
    """Get open positions"""
    if not _api_instance:
        return []
    
    try:
        if _api_type == 'mt5':
            positions = _api_instance.positions_get(symbol=symbol)
            if positions:
                return [{
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == _api_instance.POSITION_TYPE_BUY else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'sl': pos.sl,
                    'tp': pos.tp
                } for pos in positions]
            return []
            
        elif _api_type == 'mock':
            return _api_instance.positions_get(symbol)
    except Exception as e:
        logger.error(f"Error getting positions: {str(e)}")
    
    return []

def orders_get(symbol: str = None) -> List[Dict[str, Any]]:
    """Get pending orders"""
    if not _api_instance:
        return []
    
    try:
        if _api_type == 'mt5':
            orders = _api_instance.orders_get(symbol=symbol)
            if orders:
                return [{
                    'ticket': order.ticket,
                    'symbol': order.symbol,
                    'type': 'BUY' if order.type == _api_instance.ORDER_TYPE_BUY else 'SELL',
                    'volume': order.volume,
                    'price_open': order.price_open,
                    'sl': order.sl,
                    'tp': order.tp
                } for order in orders]
            return []
            
        elif _api_type == 'mock':
            return _api_instance.orders_get(symbol)
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
    
    return []

def order_delete(ticket: int) -> bool:
    """Delete pending order"""
    if not _api_instance:
        return False
    
    try:
        if _api_type == 'mt5':
            result = _api_instance.order_delete(ticket)
            return result.retcode == _api_instance.TRADE_RETCODE_DONE
        elif _api_type == 'mock':
            return _api_instance.order_delete(ticket)
    except Exception as e:
        logger.error(f"Error deleting order: {str(e)}")
    
    return False

def shutdown() -> None:
    """Shutdown API connection"""
    global _api_instance, _api_type
    
    if _api_instance:
        try:
            if _api_type == 'mt5':
                _api_instance.shutdown()
            logger.info("API connection shutdown")
        except Exception as e:
            logger.error(f"Error shutting down API: {str(e)}")
        finally:
            _api_instance = None
            _api_type = None 