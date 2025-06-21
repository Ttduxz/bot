#!/usr/bin/env python3
"""
MetaTrader5 Web API Integration for XAU/USD Scalping Bot V3
Provides MT5 functionality via Web API instead of desktop application,
making it compatible with macOS, Linux, and Windows.

This module uses the MT5 Web API to:
- Connect to MT5 accounts
- Get market data
- Place and manage orders
- Retrieve account information
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

class MT5WebAPI:
    def __init__(self, server_url: str, login: int, password: str, api_key: str = None):
        """
        Initialize MT5 Web API connection
        
        Args:
            server_url: MT5 Web API server URL (e.g., 'https://api.mt5.com')
            login: MT5 account login
            password: MT5 account password
            api_key: Optional API key for enhanced security
        """
        self.server_url = server_url.rstrip('/')
        self.login = login
        self.password = password
        self.api_key = api_key
        self.session = requests.Session()
        self.auth_token = None
        self.is_connected = False
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'XAUUSD-Scalping-Bot-V3/1.0'
        })
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def connect(self) -> bool:
        """Connect to MT5 Web API"""
        try:
            auth_data = {
                'login': self.login,
                'password': self.password,
                'type': 'manager'  # or 'client' for regular accounts
            }
            
            response = self.session.post(
                f"{self.server_url}/auth/start",
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('retcode') == 'TRADE_RETCODE_DONE':
                    self.auth_token = result.get('token')
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.is_connected = True
                    print(f"Connected to MT5 Web API: {self.server_url}")
                    return True
                else:
                    print(f"Authentication failed: {result.get('comment', 'Unknown error')}")
                    return False
            else:
                print(f"Connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5 Web API"""
        if self.auth_token:
            try:
                self.session.post(f"{self.server_url}/auth/stop")
            except:
                pass
        self.auth_token = None
        self.is_connected = False
        print("Disconnected from MT5 Web API")
    
    def get_account_info(self) -> Optional[Dict]:
        """Get account information"""
        if not self.is_connected:
            return None
            
        try:
            response = self.session.get(f"{self.server_url}/account")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get symbol information"""
        if not self.is_connected:
            return None
            
        try:
            response = self.session.get(f"{self.server_url}/symbol/{symbol}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting symbol info: {str(e)}")
            return None
    
    def get_historical_data(self, symbol: str, timeframe: str, count: int, start_pos: int = 0) -> Optional[List]:
        """
        Get historical price data
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            timeframe: Timeframe ('M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1')
            count: Number of candles to retrieve
            start_pos: Starting position (0 for latest)
        """
        if not self.is_connected:
            return None
            
        try:
            # Convert timeframe to MT5 format
            tf_map = {
                'M1': 1, 'M5': 5, 'M15': 15, 'M30': 30,
                'H1': 16385, 'H4': 16388, 'D1': 16408
            }
            mt5_timeframe = tf_map.get(timeframe, 1)
            
            params = {
                'symbol': symbol,
                'timeframe': mt5_timeframe,
                'count': count,
                'start_pos': start_pos
            }
            
            response = self.session.get(f"{self.server_url}/history", params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return None
        except Exception as e:
            print(f"Error getting historical data: {str(e)}")
            return None
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: float = None, sl: float = None, tp: float = None,
                   comment: str = "") -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol: Trading symbol
            order_type: 'BUY' or 'SELL'
            volume: Order volume in lots
            price: Order price (None for market orders)
            sl: Stop loss price
            tp: Take profit price
            comment: Order comment
        """
        if not self.is_connected:
            return None
            
        try:
            order_data = {
                'symbol': symbol,
                'type': order_type,
                'volume': volume,
                'comment': comment
            }
            
            if price:
                order_data['price'] = price
            if sl:
                order_data['sl'] = sl
            if tp:
                order_data['tp'] = tp
            
            response = self.session.post(f"{self.server_url}/order", json=order_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('retcode') == 'TRADE_RETCODE_DONE':
                    return result
                else:
                    print(f"Order failed: {result.get('comment', 'Unknown error')}")
                    return None
            return None
        except Exception as e:
            print(f"Error placing order: {str(e)}")
            return None
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """Get open positions"""
        if not self.is_connected:
            return []
            
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
                
            response = self.session.get(f"{self.server_url}/positions", params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('positions', [])
            return []
        except Exception as e:
            print(f"Error getting positions: {str(e)}")
            return []
    
    def get_orders(self, symbol: str = None) -> List[Dict]:
        """Get pending orders"""
        if not self.is_connected:
            return []
            
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol
                
            response = self.session.get(f"{self.server_url}/orders", params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('orders', [])
            return []
        except Exception as e:
            print(f"Error getting orders: {str(e)}")
            return []
    
    def close_position(self, ticket: int, volume: float = None) -> bool:
        """Close a position"""
        if not self.is_connected:
            return False
            
        try:
            close_data = {'ticket': ticket}
            if volume:
                close_data['volume'] = volume
                
            response = self.session.post(f"{self.server_url}/position/close", json=close_data)
            if response.status_code == 200:
                result = response.json()
                return result.get('retcode') == 'TRADE_RETCODE_DONE'
            return False
        except Exception as e:
            print(f"Error closing position: {str(e)}")
            return False
    
    def modify_position(self, ticket: int, sl: float = None, tp: float = None) -> bool:
        """Modify position stop loss and take profit"""
        if not self.is_connected:
            return False
            
        try:
            modify_data = {'ticket': ticket}
            if sl is not None:
                modify_data['sl'] = sl
            if tp is not None:
                modify_data['tp'] = tp
                
            response = self.session.post(f"{self.server_url}/position/modify", json=modify_data)
            if response.status_code == 200:
                result = response.json()
                return result.get('retcode') == 'TRADE_RETCODE_DONE'
            return False
        except Exception as e:
            print(f"Error modifying position: {str(e)}")
            return False

# Global MT5 Web API instance
mt5_web = None

def initialize_mt5_web(server_url: str, login: int, password: str, api_key: str = None) -> bool:
    """Initialize MT5 Web API connection"""
    global mt5_web
    mt5_web = MT5WebAPI(server_url, login, password, api_key)
    return mt5_web.connect()

def get_mt5_web() -> Optional[MT5WebAPI]:
    """Get the global MT5 Web API instance"""
    return mt5_web

# Compatibility functions to match the original MT5 API
def initialize():
    """Initialize MT5 (Web API version)"""
    if mt5_web:
        return mt5_web.is_connected
    return False

def shutdown():
    """Shutdown MT5 (Web API version)"""
    if mt5_web:
        mt5_web.disconnect()
    return True

def account_info():
    """Get account info (Web API version)"""
    if mt5_web:
        return mt5_web.get_account_info()
    return None

def symbol_info(symbol):
    """Get symbol info (Web API version)"""
    if mt5_web:
        return mt5_web.get_symbol_info(symbol)
    return None

def copy_rates_from(symbol, timeframe, start_pos, count):
    """Get historical data (Web API version)"""
    if mt5_web:
        return mt5_web.get_historical_data(symbol, timeframe, count, start_pos)
    return None

def order_send(request):
    """Send order (Web API version)"""
    if mt5_web:
        return mt5_web.place_order(**request)
    return None

def positions_get(symbol=None):
    """Get positions (Web API version)"""
    if mt5_web:
        return mt5_web.get_positions(symbol)
    return []

def orders_get(symbol=None):
    """Get orders (Web API version)"""
    if mt5_web:
        return mt5_web.get_orders(symbol)
    return [] 