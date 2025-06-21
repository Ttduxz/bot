#!/usr/bin/env python3
"""
Test script to verify all imports work correctly with the new v3 structure
"""

def test_imports():
    """Test all module imports"""
    print("Testing XAU/USD Scalping Bot V3 imports...")
    
    try:
        # Test core modules
        print("✓ Testing core modules...")
        from config import CONFIG
        from indicators import calculate_indicators
        from strategy import generate_signal
        from risk_management import risk_manager
        from trade_executor import initialize_mt5
        from logger import log_info
        from utils import get_historical_data
        print("  ✓ Core modules imported successfully")
        
        # Test v3 modules
        print("✓ Testing v3 modules...")
        from modules.mtf_filter import mtf_filter, MultiTimeframeFilter
        from modules.cooldown_manager import cooldown_manager, CooldownManager
        from modules.signal_evaluator import signal_evaluator, SignalEvaluator
        from modules.volatility_filter import volatility_filter, VolatilityFilter
        from modules.pause_manager import pause_manager, PauseManager
        print("  ✓ V3 modules imported successfully")
        
        # Test dashboard
        print("✓ Testing dashboard...")
        import streamlit as st
        import plotly.graph_objects as go
        print("  ✓ Dashboard dependencies imported successfully")
        
        # Test package imports
        print("✓ Testing package imports...")
        from modules import (
            mtf_filter, cooldown_manager, signal_evaluator, 
            volatility_filter, pause_manager
        )
        print("  ✓ Package imports successful")
        
        print("\n🎉 All imports successful! V3 structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import CONFIG
        
        required_keys = [
            'symbol', 'timeframe', 'risk_per_trade', 'max_trades_per_day',
            'max_daily_loss', 'signal_minimum_score', 'cooldown_win_minutes',
            'cooldown_loss_minutes', 'atr_sl_multiplier', 'atr_tp_multiplier'
        ]
        
        for key in required_keys:
            if key not in CONFIG:
                print(f"❌ Missing config key: {key}")
                return False
        
        print("✓ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("XAU/USD Scalping Bot V3 - Import Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test configuration
    config_ok = test_configuration()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    
    if imports_ok and config_ok:
        print("\n🎉 All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("1. Configure your MT5 credentials in .env file")
        print("2. Run 'python test_bot_v3.py' to test all components")
        print("3. Run 'python main.py' for live trading")
        print("4. Run 'streamlit run dashboard.py' for the monitoring dashboard")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 