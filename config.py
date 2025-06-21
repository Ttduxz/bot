import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    # Risk Management
    'risk_per_trade': 0.01,   # 1% risk per trade
    'max_trades_per_day': 5,
    'max_daily_loss': 0.03,   # 3% max daily loss
    'take_profit_pips': 10,
    'stop_loss_pips': 7,
    
    # Trading Parameters
    'symbol': 'XAUUSD',
    'timeframe': 'M1',  # 1-minute chart
    'magic_number': 234000,
    'deviation': 10,
    
    # Technical Indicators (Updated for v3)
    'ema_fast': 5,
    'ema_slow': 20,  # Changed from 21 to 20
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'atr_period': 14,
    
    # V3 Enhanced Parameters
    'mtf_enabled': True,  # Multi-timeframe confirmation
    'signal_minimum_score': 60,  # Minimum signal score to execute trade
    'cooldown_win_minutes': 3,  # Cooldown after winning trade
    'cooldown_loss_minutes': 10,  # Cooldown after losing trade
    'pause_none_signals': 3,  # Pause after N consecutive NONE signals
    'pause_duration_minutes': 30,  # Pause duration
    
    # ATR-based Dynamic SL/TP (Updated v3)
    'atr_sl_multiplier': 1.2,  # Stop Loss = ATR × 1.2
    'atr_tp_multiplier': 1.8,  # Take Profit = ATR × 1.8
    
    # Volatility Filter
    'min_volatility_ratio': 1.0,  # Current ATR must be >= ATR MA
    'atr_ma_period': 20,  # Period for ATR moving average
    
    # MACD Parameters
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    
    # Trading Sessions (UTC)
    'london_open': '08:00',
    'london_close': '16:00',
    'newyork_open': '13:00',
    'newyork_close': '21:00',
    
    # MT5 Connection
    'mt5_login': int(os.getenv('MT5_LOGIN', '0')),
    'mt5_password': os.getenv('MT5_PASSWORD', ''),
    'mt5_server': os.getenv('MT5_SERVER', ''),
    
    # Logging
    'log_file': 'trading_bot_v3.log',
    'trade_log_file': 'trade_log_v3.csv',
    'signal_log_file': 'signal_log_v3.csv',
    
    # Backtesting
    'backtest_start_date': '2024-01-01',
    'backtest_end_date': '2024-12-31',
    'commission_per_lot': 7.0,  # USD per lot
    'slippage_pips': 1,
    
    # V3 Performance Tracking
    'enable_signal_scoring': True,
    'enable_volatility_filter': True,
    'enable_momentum_filter': True,
    'enable_auto_pause': True,
    'enable_cooldown': True,
} 