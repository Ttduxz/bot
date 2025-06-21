#!/usr/bin/env python3
"""
Configuration Module for XAU/USD Scalping Bot V3
Centralized configuration management with enhanced v3 parameters
and comprehensive settings for all bot components.

TODO LIST:
1. TODO: Implement configuration validation system
   - Add parameter type checking
   - Implement range validation for numeric parameters
   - Add dependency validation between parameters
   - Include configuration schema validation

2. TODO: Add environment-based configuration
   - Implement environment-specific config files
   - Add development/production configuration switching
   - Include sensitive data encryption
   - Add configuration backup/restore functionality

3. TODO: Implement dynamic configuration updates
   - Add runtime configuration modification
   - Implement configuration hot-reloading
   - Add configuration change logging
   - Include configuration version control

4. TODO: Add configuration optimization tools
   - Implement configuration performance analysis
   - Add parameter sensitivity testing
   - Include configuration benchmarking
   - Add automated configuration tuning

5. TODO: Implement configuration security
   - Add configuration encryption
   - Implement access control for sensitive settings
   - Include configuration audit logging
   - Add configuration integrity checks

6. TODO: Add configuration documentation
   - Implement auto-generated configuration docs
   - Add parameter usage examples
   - Include configuration best practices
   - Add configuration troubleshooting guide

7. TODO: Implement configuration testing framework
   - Add configuration unit tests
   - Implement configuration integration tests
   - Include configuration validation tests
   - Add configuration performance tests

8. TODO: Add configuration monitoring
   - Implement configuration usage tracking
   - Add configuration performance metrics
   - Include configuration error monitoring
   - Add configuration health checks

9. TODO: Implement configuration migration system
   - Add configuration version migration
   - Implement backward compatibility
   - Include configuration upgrade tools
   - Add configuration rollback functionality

10. TODO: Add configuration analytics
    - Implement configuration usage analytics
    - Add configuration performance analysis
    - Include configuration optimization suggestions
    - Add configuration impact assessment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Trading Configuration
SYMBOL = 'XAUUSD'
TIMEFRAME = 'M1'
SECONDARY_TIMEFRAME = 'M5'

# Indicator Settings
EMA_FAST = 5
EMA_SLOW = 21
EMA_FAST_M5 = 5
EMA_SLOW_M5 = 20
RSI_PERIOD = 14
ATR_PERIOD = 14

# Risk Management
MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '100'))
MAX_DAILY_TRADES = int(os.getenv('MAX_DAILY_TRADES', '10'))
RISK_PERCENT = float(os.getenv('RISK_PERCENT', '2.0'))
POSITION_SIZE = float(os.getenv('POSITION_SIZE', '0.1'))

# ATR-based SL/TP
ATR_SL_MULTIPLIER = 1.2
ATR_TP_MULTIPLIER = 1.8

# Cooldown Settings
COOLDOWN_WIN_MINUTES = 3
COOLDOWN_LOSS_MINUTES = 10

# Signal Quality
MIN_SIGNAL_SCORE = 60

# Volatility Filter
ATR_MA_PERIOD = 20
VOLATILITY_THRESHOLD = 0.5

# Momentum Filter
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Auto Pause
MAX_CONSECUTIVE_NONE = 3

# MT5 Configuration
MT5_LOGIN = os.getenv('MT5_LOGIN')
MT5_PASSWORD = os.getenv('MT5_PASSWORD')
MT5_SERVER = os.getenv('MT5_SERVER')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'trading_bot_v3.log'

# Debug Mode
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Configuration dictionary
CONFIG = {
    'symbol': SYMBOL,
    'timeframe': TIMEFRAME,
    'secondary_timeframe': SECONDARY_TIMEFRAME,
    'ema_fast': EMA_FAST,
    'ema_slow': EMA_SLOW,
    'ema_fast_m5': EMA_FAST_M5,
    'ema_slow_m5': EMA_SLOW_M5,
    'rsi_period': RSI_PERIOD,
    'atr_period': ATR_PERIOD,
    'max_daily_loss': MAX_DAILY_LOSS,
    'max_daily_trades': MAX_DAILY_TRADES,
    'risk_percent': RISK_PERCENT,
    'position_size': POSITION_SIZE,
    'atr_sl_multiplier': ATR_SL_MULTIPLIER,
    'atr_tp_multiplier': ATR_TP_MULTIPLIER,
    'cooldown_win_minutes': COOLDOWN_WIN_MINUTES,
    'cooldown_loss_minutes': COOLDOWN_LOSS_MINUTES,
    'min_signal_score': MIN_SIGNAL_SCORE,
    'atr_ma_period': ATR_MA_PERIOD,
    'volatility_threshold': VOLATILITY_THRESHOLD,
    'macd_fast': MACD_FAST,
    'macd_slow': MACD_SLOW,
    'macd_signal': MACD_SIGNAL,
    'max_consecutive_none': MAX_CONSECUTIVE_NONE,
    'mt5_login': MT5_LOGIN,
    'mt5_password': MT5_PASSWORD,
    'mt5_server': MT5_SERVER,
    'log_level': LOG_LEVEL,
    'log_file': LOG_FILE,
    'debug': DEBUG
} 