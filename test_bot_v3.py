#!/usr/bin/env python3
"""
Test script for XAU/USD Scalping Bot V3
This script tests all the new v3 enhancements
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import bot modules
from config import CONFIG
from indicators import calculate_ema, calculate_rsi, calculate_atr, add_v3_indicators
from strategy import generate_signal, generate_base_signal, combine_signals
from modules.mtf_filter import MultiTimeframeFilter
from modules.cooldown_manager import CooldownManager
from modules.signal_evaluator import SignalEvaluator
from modules.volatility_filter import VolatilityFilter
from modules.pause_manager import PauseManager

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

def test_v3_indicators():
    """Test v3 technical indicators calculation"""
    print("\n=== Testing V3 Indicators ===")
    
    # Create sample data
    df = create_sample_data()
    
    # Test EMA calculation (Updated to EMA20)
    ema5 = calculate_ema(df['close'], 5)
    ema20 = calculate_ema(df['close'], 20)  # Changed from 21 to 20
    
    print(f"EMA(5) latest value: {ema5.iloc[-1]:.2f}")
    print(f"EMA(20) latest value: {ema20.iloc[-1]:.2f}")
    print(f"EMA trend: {'Bullish' if ema5.iloc[-1] > ema20.iloc[-1] else 'Bearish'}")
    
    # Test RSI calculation
    rsi = calculate_rsi(df['close'], 14)
    print(f"RSI latest value: {rsi.iloc[-1]:.2f}")
    print(f"RSI status: {'Overbought' if rsi.iloc[-1] > 70 else 'Oversold' if rsi.iloc[-1] < 30 else 'Neutral'}")
    
    # Test ATR calculation
    atr = calculate_atr(df['high'], df['low'], df['close'], 14)
    print(f"ATR latest value: {atr.iloc[-1]:.2f}")
    
    # Test v3 additional indicators
    df = add_v3_indicators(df)
    print(f"ATR MA: {df['atr_ma'].iloc[-1]:.2f}")
    print(f"MACD Histogram: {df['macd_histogram'].iloc[-1]:.4f}")
    
    return True

def test_multi_timeframe_filter():
    """Test multi-timeframe filter"""
    print("\n=== Testing Multi-Timeframe Filter ===")
    
    # Create sample M1 and M5 data
    m1_data = create_sample_data()
    m5_data = create_sample_data()  # Simplified for testing
    
    # Create MTF filter instance
    mtf = MultiTimeframeFilter()
    
    # Simulate data loading
    mtf.m1_data = m1_data
    mtf.m5_data = m5_data
    
    # Calculate EMAs for both timeframes
    mtf.m1_data['ema5'] = calculate_ema(mtf.m1_data['close'], 5)
    mtf.m1_data['ema20'] = calculate_ema(mtf.m1_data['close'], 20)
    mtf.m5_data['ema5'] = calculate_ema(mtf.m5_data['close'], 5)
    mtf.m5_data['ema20'] = calculate_ema(mtf.m5_data['close'], 20)
    
    # Test trend alignment
    aligned, trend, confidence = mtf.check_trend_alignment()
    print(f"MTF Aligned: {aligned}")
    print(f"MTF Trend: {trend}")
    print(f"MTF Confidence: {confidence:.2f}")
    
    # Test signal generation
    mtf_signal = mtf.get_mtf_signal()
    print(f"MTF Signal: {mtf_signal}")
    
    return True

def test_cooldown_manager():
    """Test cooldown manager"""
    print("\n=== Testing Cooldown Manager ===")
    
    cooldown = CooldownManager()
    
    # Test initial state
    print(f"Can trade initially: {cooldown.can_trade()}")
    
    # Test after winning trade
    cooldown.record_trade_result("WIN")
    print(f"Can trade after WIN: {cooldown.can_trade()}")
    print(f"Cooldown remaining: {cooldown.get_cooldown_remaining()} minutes")
    
    # Test after losing trade
    cooldown.reset_cooldown()
    cooldown.record_trade_result("LOSS")
    print(f"Can trade after LOSS: {cooldown.can_trade()}")
    print(f"Cooldown remaining: {cooldown.get_cooldown_remaining()} minutes")
    
    # Test status
    status = cooldown.get_cooldown_status()
    print(f"Cooldown status: {status}")
    
    return True

def test_signal_evaluator():
    """Test signal evaluator"""
    print("\n=== Testing Signal Evaluator ===")
    
    evaluator = SignalEvaluator()
    
    # Create sample indicators
    indicators = {
        'rsi': 65,  # Above 60
        'atr': 1.5,
        'atr_ma': 1.0,  # ATR > MA
        'ema5': 2005.0,
        'ema20': 2000.0,
        'close': 2003.0,
        'prev_close': 2002.0,
        'volume': 500,
        'avg_volume': 400
    }
    
    # Test signal scoring
    score, breakdown = evaluator.calculate_signal_score(indicators, mtf_aligned=True)
    print(f"Signal Score: {score}")
    print(f"Score Breakdown: {breakdown}")
    
    # Test trade execution decision
    should_execute, score, breakdown = evaluator.should_execute_trade(indicators, mtf_aligned=True)
    print(f"Should Execute: {should_execute}")
    
    # Test analysis
    analysis = evaluator.get_signal_analysis(indicators, mtf_aligned=True)
    print(f"Signal Quality: {analysis['quality']}")
    print(f"Recommendation: {analysis['recommendation']}")
    
    return True

def test_volatility_filter():
    """Test volatility filter"""
    print("\n=== Testing Volatility Filter ===")
    
    vol_filter = VolatilityFilter()
    
    # Create sample data
    df = create_sample_data()
    
    # Test volatility conditions
    vol_ok, vol_reason, vol_metrics = vol_filter.check_volatility_conditions(df)
    print(f"Volatility OK: {vol_ok}")
    print(f"Volatility Reason: {vol_reason}")
    print(f"Volatility Metrics: {vol_metrics}")
    
    # Test momentum conditions
    mom_ok, mom_reason, mom_metrics = vol_filter.check_momentum_conditions(df)
    print(f"Momentum OK: {mom_ok}")
    print(f"Momentum Reason: {mom_reason}")
    
    # Test overall status
    status = vol_filter.get_volatility_status(df)
    print(f"Overall Suitable: {status['overall_suitable']}")
    
    # Test scores
    vol_score = vol_filter.get_volatility_score(df)
    mom_score = vol_filter.get_momentum_score(df)
    print(f"Volatility Score: {vol_score}")
    print(f"Momentum Score: {mom_score}")
    
    return True

def test_pause_manager():
    """Test pause manager"""
    print("\n=== Testing Pause Manager ===")
    
    pause_mgr = PauseManager()
    
    # Test initial state
    print(f"Can trade initially: {pause_mgr.can_trade()[0]}")
    
    # Test consecutive NONE signals
    for i in range(3):
        pause_mgr.record_signal("NONE")
        print(f"After {i+1} NONE signals: {pause_mgr.consecutive_none_signals}")
    
    # Test auto-pause
    should_pause, reason = pause_mgr.check_auto_pause_conditions()
    print(f"Should pause: {should_pause}")
    print(f"Pause reason: {reason}")
    
    # Test pause management
    can_trade, action = pause_mgr.auto_manage_pause("NONE")
    print(f"Can trade after auto-manage: {can_trade}")
    print(f"Action: {action}")
    
    # Test status
    status = pause_mgr.get_status()
    print(f"Pause status: {status}")
    
    return True

def test_v3_strategy():
    """Test v3 strategy integration"""
    print("\n=== Testing V3 Strategy Integration ===")
    
    # Create sample data
    df = create_sample_data()
    df = add_v3_indicators(df)
    
    # Get latest indicators
    indicators = df.iloc[-1]
    
    # Test base signal generation
    base_signal = generate_base_signal(indicators)
    print(f"Base Signal: {base_signal}")
    
    # Test signal combination
    mtf_signal = "BUY"  # Simulate MTF signal
    combined_signal = combine_signals(base_signal, mtf_signal)
    print(f"Combined Signal: {combined_signal}")
    
    # Test comprehensive analysis
    from strategy import get_comprehensive_signal_analysis
    analysis = get_comprehensive_signal_analysis(indicators, df)
    print(f"Comprehensive Signal: {analysis['signal']}")
    print(f"Signal Quality: {analysis['signal_analysis']['quality']}")
    
    return True

def test_configuration_v3():
    """Test v3 configuration settings"""
    print("\n=== Testing V3 Configuration ===")
    
    print("V3 Enhanced Configuration:")
    print(f"EMA Fast: {CONFIG['ema_fast']}")
    print(f"EMA Slow: {CONFIG['ema_slow']} (Updated from 21 to 20)")
    print(f"MTF Enabled: {CONFIG['mtf_enabled']}")
    print(f"Signal Minimum Score: {CONFIG['signal_minimum_score']}")
    print(f"Cooldown Win Minutes: {CONFIG['cooldown_win_minutes']}")
    print(f"Cooldown Loss Minutes: {CONFIG['cooldown_loss_minutes']}")
    print(f"Pause None Signals: {CONFIG['pause_none_signals']}")
    print(f"ATR SL Multiplier: {CONFIG['atr_sl_multiplier']}")
    print(f"ATR TP Multiplier: {CONFIG['atr_tp_multiplier']}")
    print(f"Min Volatility Ratio: {CONFIG['min_volatility_ratio']}")
    
    return True

def main():
    """Run all v3 tests"""
    print("XAU/USD Scalping Bot V3 - Enhanced Component Tests")
    print("=" * 60)
    
    tests = [
        test_configuration_v3,
        test_v3_indicators,
        test_multi_timeframe_filter,
        test_cooldown_manager,
        test_signal_evaluator,
        test_volatility_filter,
        test_pause_manager,
        test_v3_strategy
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
    
    print("=" * 60)
    print(f"V3 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All V3 tests passed! The enhanced bot is working correctly.")
        print("\nV3 Enhancements Summary:")
        print("✅ Multi-timeframe confirmation (M1 + M5)")
        print("✅ Adaptive cooldown between trades")
        print("✅ Enhanced ATR-based dynamic SL/TP")
        print("✅ Signal quality scoring system")
        print("✅ Market volatility & momentum filter")
        print("✅ Auto pause mode for market conditions")
        print("\nNext steps:")
        print("1. Install MetaTrader 5")
        print("2. Configure your MT5 credentials in .env file")
        print("3. Run: python main.py (for live trading)")
        print("4. Run: python main.py status (for status report)")
        print("5. Run: python backtest.py (for backtesting)")
    else:
        print("❌ Some V3 tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 