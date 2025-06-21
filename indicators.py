import pandas as pd
import numpy as np
from config import CONFIG

def calculate_ema(series, period):
    """
    Calculate Exponential Moving Average
    """
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series, period=14):
    """
    Calculate Relative Strength Index
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(high, low, close, period=14):
    """
    Calculate Average True Range
    """
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def calculate_indicators(rates):
    """
    Calculate all technical indicators for the strategy (Updated for v3)
    Returns the latest indicators row
    """
    df = pd.DataFrame(rates)
    df['close'] = df['close']
    df['high'] = df['high']
    df['low'] = df['low']
    
    # Calculate EMAs (Updated: EMA20 instead of EMA21)
    df['ema5'] = calculate_ema(df['close'], 5)
    df['ema20'] = calculate_ema(df['close'], 20)  # Changed from 21 to 20
    
    # Calculate RSI
    df['rsi'] = calculate_rsi(df['close'], CONFIG['rsi_period'])
    
    # Calculate ATR
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'], CONFIG['atr_period'])
    
    # Add additional indicators for v3
    df = add_v3_indicators(df)
    
    return df.iloc[-1]  # Return latest indicators row

def add_v3_indicators(df):
    """
    Add additional indicators required for v3 strategy
    """
    # ATR Moving Average (20-period)
    df['atr_ma'] = df['atr'].rolling(window=20).mean()
    
    # Volume moving average if available
    if 'tick_volume' in df.columns:
        df['avg_volume'] = df['tick_volume'].rolling(window=20).mean()
    
    # Previous close for momentum calculation
    df['prev_close'] = df['close'].shift(1)
    
    # MACD components
    df['ema12'] = calculate_ema(df['close'], 12)
    df['ema26'] = calculate_ema(df['close'], 26)
    df['macd_line'] = df['ema12'] - df['ema26']
    df['macd_signal'] = calculate_ema(df['macd_line'], 9)
    df['macd_histogram'] = df['macd_line'] - df['macd_signal']
    
    return df

def get_volatility_filter(atr_value, atr_period=14):
    """
    Check if market volatility is sufficient for trading
    """
    # Simple volatility filter - can be enhanced
    return atr_value > 0.5  # Minimum ATR threshold

def calculate_multi_timeframe_indicators(m1_data, m5_data):
    """
    Calculate indicators for both M1 and M5 timeframes
    """
    if m1_data is None or m5_data is None:
        return None, None
    
    # Calculate indicators for M1
    m1_indicators = calculate_indicators(m1_data)
    
    # Calculate indicators for M5
    m5_indicators = calculate_indicators(m5_data)
    
    return m1_indicators, m5_indicators

def get_trend_strength(ema_fast, ema_slow, close_price):
    """
    Calculate trend strength based on EMA separation
    """
    if ema_slow == 0:
        return 0
    
    ema_diff = abs(ema_fast - ema_slow)
    trend_strength = ema_diff / ema_slow
    
    return trend_strength

def get_momentum_score(close_prices, period=5):
    """
    Calculate momentum score based on price changes
    """
    if len(close_prices) < period + 1:
        return 0
    
    # Calculate price changes over the period
    price_changes = close_prices.diff(period)
    
    # Calculate momentum as percentage change
    momentum = (price_changes / close_prices.shift(period)) * 100
    
    # Get latest momentum value
    latest_momentum = momentum.iloc[-1]
    
    return latest_momentum if not pd.isna(latest_momentum) else 0 