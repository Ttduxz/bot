#!/usr/bin/env python3
"""
Mock MetaTrader5 Module for Non-Windows Systems
Provides mock implementations of MT5 functions for backtesting and development
on macOS/Linux systems where the real MetaTrader5 library is not available.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Mock constants
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 16385
TIMEFRAME_H4 = 16388
TIMEFRAME_D1 = 16408

# Mock order types
ORDER_TYPE_BUY = 0
ORDER_TYPE_SELL = 1
ORDER_TYPE_BUY_LIMIT = 2
ORDER_TYPE_SELL_LIMIT = 3
ORDER_TYPE_BUY_STOP = 4
ORDER_TYPE_SELL_STOP = 5

# Mock return codes
TRADE_RETCODE_DONE = 10009
TRADE_RETCODE_REQUOTE = 10004
TRADE_RETCODE_REJECT = 10004
TRADE_RETCODE_CANCEL = 10027

def initialize():
    """Mock MT5 initialization"""
    print("Mock MT5 initialized (for backtesting/development)")
    return True

def shutdown():
    """Mock MT5 shutdown"""
    print("Mock MT5 shutdown")
    return True

def login(login, password, server):
    """Mock MT5 login"""
    print(f"Mock MT5 login: {login}@{server}")
    return True

def account_info():
    """Mock account info"""
    class MockAccountInfo:
        def __init__(self):
            self.login = 12345678
            self.balance = 10000.0
            self.equity = 10150.0
            self.profit = 150.0
            self.margin = 1000.0
            self.margin_level = 85.0
            self.currency = "USD"
    
    return MockAccountInfo()

def symbol_info(symbol):
    """Mock symbol info"""
    class MockSymbolInfo:
        def __init__(self, symbol):
            self.name = symbol
            self.bid = 2000.0
            self.ask = 2000.1
            self.point = 0.01
            self.digits = 2
            self.spread = 10
            self.trade_mode = 4  # TRADE_MODE_FULL
    
    return MockSymbolInfo(symbol)

def copy_rates_from(symbol, timeframe, start_pos, count):
    """Mock historical data retrieval"""
    # Generate mock price data
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=count)
    
    dates = pd.date_range(start=start_date, end=end_date, periods=count)
    
    # Generate realistic price data
    base_price = 2000.0
    prices = []
    for i in range(count):
        # Add some trend and noise
        trend = np.sin(i * 0.1) * 5
        noise = np.random.normal(0, 0.5)
        price = base_price + trend + noise
        
        # Create OHLC data
        high = price + abs(np.random.normal(0, 0.3))
        low = price - abs(np.random.normal(0, 0.3))
        open_price = price + np.random.normal(0, 0.2)
        close_price = price
        
        prices.append({
            'time': int(dates[i].timestamp()),
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
            'tick_volume': np.random.randint(100, 1000),
            'spread': 10,
            'real_volume': np.random.randint(100, 1000)
        })
    
    return prices

def copy_rates_from_pos(symbol, timeframe, start_pos, count):
    """Mock historical data retrieval from position"""
    return copy_rates_from(symbol, timeframe, start_pos, count)

def order_send(request):
    """Mock order sending"""
    class MockOrderResult:
        def __init__(self):
            self.retcode = TRADE_RETCODE_DONE
            self.order = 12345
            self.volume = request.get('volume', 0.1)
            self.price = request.get('price', 2000.0)
            self.bid = 2000.0
            self.ask = 2000.1
            self.comment = "Mock order"
            self.request_id = 1
            self.retcode_external = 0
    
    return MockOrderResult()

def positions_get(symbol=None):
    """Mock positions retrieval"""
    return []

def orders_get(symbol=None):
    """Mock orders retrieval"""
    return []

def terminal_info():
    """Mock terminal info"""
    class MockTerminalInfo:
        def __init__(self):
            self.trade_allowed = True
            self.connected = True
            self.trade_mode = 4  # TRADE_MODE_FULL
    
    return MockTerminalInfo()

def symbol_select(symbol, enable):
    """Mock symbol selection"""
    return True

def market_book_get(symbol):
    """Mock market book retrieval"""
    return []

# Create a mock module that can be imported
class MockMT5:
    def __init__(self):
        self.TIMEFRAME_M1 = TIMEFRAME_M1
        self.TIMEFRAME_M5 = TIMEFRAME_M5
        self.TIMEFRAME_M15 = TIMEFRAME_M15
        self.TIMEFRAME_M30 = TIMEFRAME_M30
        self.TIMEFRAME_H1 = TIMEFRAME_H1
        self.TIMEFRAME_H4 = TIMEFRAME_H4
        self.TIMEFRAME_D1 = TIMEFRAME_D1
        
        self.ORDER_TYPE_BUY = ORDER_TYPE_BUY
        self.ORDER_TYPE_SELL = ORDER_TYPE_SELL
        self.ORDER_TYPE_BUY_LIMIT = ORDER_TYPE_BUY_LIMIT
        self.ORDER_TYPE_SELL_LIMIT = ORDER_TYPE_SELL_LIMIT
        self.ORDER_TYPE_BUY_STOP = ORDER_TYPE_BUY_STOP
        self.ORDER_TYPE_SELL_STOP = ORDER_TYPE_SELL_STOP
        
        self.TRADE_RETCODE_DONE = TRADE_RETCODE_DONE
        self.TRADE_RETCODE_REQUOTE = TRADE_RETCODE_REQUOTE
        self.TRADE_RETCODE_REJECT = TRADE_RETCODE_REJECT
        self.TRADE_RETCODE_CANCEL = TRADE_RETCODE_CANCEL

# Export all functions and constants
__all__ = [
    'initialize', 'shutdown', 'login', 'account_info', 'symbol_info',
    'copy_rates_from', 'copy_rates_from_pos', 'order_send', 'positions_get',
    'orders_get', 'terminal_info', 'symbol_select', 'market_book_get',
    'TIMEFRAME_M1', 'TIMEFRAME_M5', 'TIMEFRAME_M15', 'TIMEFRAME_M30',
    'TIMEFRAME_H1', 'TIMEFRAME_H4', 'TIMEFRAME_D1',
    'ORDER_TYPE_BUY', 'ORDER_TYPE_SELL', 'ORDER_TYPE_BUY_LIMIT',
    'ORDER_TYPE_SELL_LIMIT', 'ORDER_TYPE_BUY_STOP', 'ORDER_TYPE_SELL_STOP',
    'TRADE_RETCODE_DONE', 'TRADE_RETCODE_REQUOTE', 'TRADE_RETCODE_REJECT',
    'TRADE_RETCODE_CANCEL'
] 