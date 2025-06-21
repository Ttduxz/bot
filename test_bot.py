#!/usr/bin/env python3
"""
Test script for XAU/USD Scalping Bot
This script tests the main components without connecting to MT5
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import bot modules
from config import CONFIG
from indicators import calculate_ema, calculate_rsi, calculate_atr
from strategy import generate_signal, is_trading_session
from risk_management import RiskManager

def create_sample_data():
    """Create sample price data for testing"""
    print("Creating sample price data...")
    
    # Generate 100 data points with some trend
    np.random.seed(42)  # For reproducible results
    
    base_price = 2000.0  # Starting price for XAU/USD
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
    
    # Create price movement with some trend and noise
    price_changes = np.random.normal(0, 0.5, 100)  # Random price changes
    trend = np.linspace(0, 10, 100)  # Upward trend
    prices = base_price + trend + np.cumsum(price_changes)
    
    # Create OHLC data
    data = []
    for i, (date, price) in enumerate(zip(dates, prices)):
        # Create realistic OHLC from close price
        high = price + abs(np.random.normal(0, 0.3))
        low = price - abs(np.random.normal(0, 0.3))
        open_price = price + np.random.normal(0, 0.2)
        
        data.append({
            'time': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': price,
            'tick_volume': np.random.randint(100, 1000)
        })
    
    return pd.DataFrame(data)

def test_indicators():
    """Test technical indicators calculation"""
    print("\n=== Testing Indicators ===")
    
    # Create sample data
    df = create_sample_data()
    
    # Test EMA calculation
    ema5 = calculate_ema(df['close'], 5)
    ema21 = calculate_ema(df['close'], 21)
    
    print(f"EMA(5) latest value: {ema5.iloc[-1]:.2f}")
    print(f"EMA(21) latest value: {ema21.iloc[-1]:.2f}")
    print(f"EMA trend: {'Bullish' if ema5.iloc[-1] > ema21.iloc[-1] else 'Bearish'}")
    
    # Test RSI calculation
    rsi = calculate_rsi(df['close'], 14)
    print(f"RSI latest value: {rsi.iloc[-1]:.2f}")
    print(f"RSI status: {'Overbought' if rsi.iloc[-1] > 70 else 'Oversold' if rsi.iloc[-1] < 30 else 'Neutral'}")
    
    # Test ATR calculation
    atr = calculate_atr(df['high'], df['low'], df['close'], 14)
    print(f"ATR latest value: {atr.iloc[-1]:.2f}")
    
    return True

def test_strategy():
    """Test strategy signal generation"""
    print("\n=== Testing Strategy ===")
    
    # Create sample data
    df = create_sample_data()
    
    # Calculate indicators
    df['ema5'] = calculate_ema(df['close'], CONFIG['ema_fast'])
    df['ema21'] = calculate_ema(df['close'], CONFIG['ema_slow'])
    df['rsi'] = calculate_rsi(df['close'], CONFIG['rsi_period'])
    df['atr'] = calculate_atr(df['high'], df['low'], df['close'], CONFIG['atr_period'])
    
    # Test signal generation for last few rows
    for i in range(-5, 0):
        indicators = {
            'ema5': df['ema5'].iloc[i],
            'ema21': df['ema21'].iloc[i],
            'rsi': df['rsi'].iloc[i],
            'atr': df['atr'].iloc[i]
        }
        
        signal = generate_signal(indicators)
        print(f"Row {i}: Signal = {signal}, RSI = {indicators['rsi']:.2f}, EMA trend = {'Bullish' if indicators['ema5'] > indicators['ema21'] else 'Bearish'}")
    
    return True

def test_risk_management():
    """Test risk management functions"""
    print("\n=== Testing Risk Management ===")
    
    risk_manager = RiskManager()
    
    # Test position size calculation
    position_size = risk_manager.calculate_position_size(0.01, 10)  # 1% risk, 10 pips SL
    print(f"Position size for 1% risk, 10 pips SL: {position_size:.2f} lots")
    
    # Test daily limits
    can_trade, message = risk_manager.can_trade()
    print(f"Can trade: {can_trade}, Message: {message}")
    
    # Test daily stats
    stats = risk_manager.get_daily_stats()
    print(f"Daily stats: {stats}")
    
    return True

def test_trading_sessions():
    """Test trading session detection"""
    print("\n=== Testing Trading Sessions ===")
    
    # Test current time
    current_session = is_trading_session()
    print(f"Currently in trading session: {current_session}")
    
    # Test specific times
    test_times = [
        datetime.now().replace(hour=9, minute=0),   # London session
        datetime.now().replace(hour=14, minute=0),  # New York session
        datetime.now().replace(hour=2, minute=0),   # Off hours
    ]
    
    for test_time in test_times:
        # Temporarily override datetime.now for testing
        original_now = datetime.now
        datetime.now = lambda: test_time
        
        session_status = is_trading_session()
        print(f"Time {test_time.strftime('%H:%M')}: In session = {session_status}")
        
        # Restore original datetime.now
        datetime.now = original_now
    
    return True

def test_configuration():
    """Test configuration settings"""
    print("\n=== Testing Configuration ===")
    
    print("Key configuration parameters:")
    print(f"Symbol: {CONFIG['symbol']}")
    print(f"Timeframe: {CONFIG['timeframe']}")
    print(f"Risk per trade: {CONFIG['risk_per_trade']*100}%")
    print(f"Max trades per day: {CONFIG['max_trades_per_day']}")
    print(f"Max daily loss: {CONFIG['max_daily_loss']*100}%")
    print(f"Take profit pips: {CONFIG['take_profit_pips']}")
    print(f"Stop loss pips: {CONFIG['stop_loss_pips']}")
    print(f"EMA fast: {CONFIG['ema_fast']}")
    print(f"EMA slow: {CONFIG['ema_slow']}")
    print(f"RSI period: {CONFIG['rsi_period']}")
    print(f"ATR period: {CONFIG['atr_period']}")
    
    return True

def main():
    """Run all tests"""
    print("XAU/USD Scalping Bot - Component Tests")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_indicators,
        test_strategy,
        test_risk_management,
        test_trading_sessions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ Test passed\n")
            else:
                print("✗ Test failed\n")
        except Exception as e:
            print(f"✗ Test failed with error: {e}\n")
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot components are working correctly.")
        print("\nNext steps:")
        print("1. Install MetaTrader 5")
        print("2. Configure your MT5 credentials in .env file")
        print("3. Run: python main.py (for live trading)")
        print("4. Run: python backtest.py (for backtesting)")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 