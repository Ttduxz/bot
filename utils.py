import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from config import CONFIG

def get_mt5_timeframe(timeframe_str):
    """
    Convert timeframe string to MT5 timeframe constant
    """
    timeframe_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
    }
    return timeframe_map.get(timeframe_str, mt5.TIMEFRAME_M1)

def get_historical_data(symbol, timeframe, count=100):
    """
    Get historical price data from MT5
    """
    mt5_timeframe = get_mt5_timeframe(timeframe)
    rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
    
    if rates is None:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def get_historical_data_range(symbol, timeframe, start_date, end_date):
    """
    Get historical data for a specific date range
    """
    mt5_timeframe = get_mt5_timeframe(timeframe)
    
    # Convert dates to MT5 format
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    rates = mt5.copy_rates_range(symbol, mt5_timeframe, start_dt, end_dt)
    
    if rates is None:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def format_price(price, digits=2):
    """
    Format price to appropriate decimal places
    """
    return round(price, digits)

def calculate_pips(entry_price, exit_price, is_buy=True):
    """
    Calculate pips between entry and exit prices
    """
    if is_buy:
        pips = (exit_price - entry_price) * 10  # For XAUUSD, 1 pip = 0.1
    else:
        pips = (entry_price - exit_price) * 10
    
    return round(pips, 1)

def calculate_profit_loss(entry_price, exit_price, volume, is_buy=True):
    """
    Calculate profit/loss in USD
    """
    if is_buy:
        profit = (exit_price - entry_price) * volume * 100  # For XAUUSD
    else:
        profit = (entry_price - exit_price) * volume * 100
    
    return round(profit, 2)

def is_market_open():
    """
    Check if the market is currently open
    """
    # For forex, market is open 24/5 (Monday-Friday)
    now = datetime.now()
    
    # Check if it's weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    return True

def get_account_info():
    """
    Get MT5 account information
    """
    account_info = mt5.account_info()
    if account_info is None:
        return None
    
    return {
        'login': account_info.login,
        'balance': account_info.balance,
        'equity': account_info.equity,
        'margin': account_info.margin,
        'free_margin': account_info.margin_free,
        'profit': account_info.profit,
        'currency': account_info.currency
    }

def print_account_summary():
    """
    Print account summary information
    """
    account_info = get_account_info()
    if account_info is None:
        print("Could not retrieve account information")
        return
    
    print("\n=== Account Summary ===")
    print(f"Login: {account_info['login']}")
    print(f"Balance: ${account_info['balance']:.2f}")
    print(f"Equity: ${account_info['equity']:.2f}")
    print(f"Profit: ${account_info['profit']:.2f}")
    print(f"Free Margin: ${account_info['free_margin']:.2f}")
    print(f"Currency: {account_info['currency']}")
    print("=====================\n")

def wait_for_next_minute():
    """
    Wait until the start of the next minute
    """
    now = datetime.now()
    next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    wait_seconds = (next_minute - now).total_seconds()
    
    if wait_seconds > 0:
        import time
        time.sleep(wait_seconds) 