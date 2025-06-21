# XAU/USD Scalping Bot V3

> **For a full user manual and step-by-step instructions, see [MANUAL.md](./MANUAL.md). This README provides a technical and feature overview.**

A professional scalping bot for trading Gold (XAU/USD) using MetaTrader 5 and Python. This bot implements a sophisticated scalping strategy with comprehensive risk management, multi-timeframe analysis, advanced filtering systems, and real-time monitoring dashboard.

## 🚀 V3 Enhancements

### **Multi-Timeframe Confirmation**
- **M1 + M5 Analysis**: Confirms trends on both 1-minute and 5-minute charts
- **EMA(5) & EMA(20)**: Used on both timeframes for trend alignment
- **Signal Quality**: Only trades when both timeframes agree

### **Adaptive Cooldown System**
- **After Winning Trade**: 3-minute cooldown
- **After Losing Trade**: 10-minute cooldown
- **Emotional Control**: Prevents overtrading and revenge trading

### **Enhanced ATR-Based Dynamic SL/TP**
- **Stop Loss**: ATR × 1.2 (more conservative)
- **Take Profit**: ATR × 1.8 (better risk-reward)
- **Volatility Adaptation**: Automatically adjusts to market conditions

### **Signal Quality Scoring System**
- **Minimum Score**: 60/100 required to execute trades
- **Scoring Factors**:
  - RSI distance from 50 (+10 points)
  - ATR volatility (+15 points)
  - Multi-timeframe confirmation (+20 points)
  - Trend strength (+10 points)
  - Price momentum (+5 points)
  - Volume confirmation (+5 points)
  - Trading session bonus (+5 points)

### **Market Volatility & Momentum Filter**
- **ATR Filter**: Only trades when ATR > 20-period average
- **MACD Momentum**: Confirms directional momentum
- **Low Volatility Protection**: Avoids sideways markets

### **Auto Pause Mode**
- **3 Consecutive NONE Signals**: Automatically pauses for 30 minutes
- **Session Management**: Tracks trading sessions and performance
- **Market Responsiveness**: Resumes when conditions improve

### **Real-Time Monitoring Dashboard**
- **Live Market Data**: Current price, indicators, and signals
- **Performance Metrics**: P&L, win rate, account balance, drawdown
- **Alerts & Warnings**: Daily loss limits, cooldown status, pause conditions
- **Trade History**: Recent trades with timestamps and results
- **Signal Analysis**: Quality breakdown and filter status
- **Auto-Refresh**: Configurable refresh intervals (1-30 seconds)
- **Mode Switching**: Live trading and backtest modes

## Features

- **Scalping Strategy**: 1-minute timeframe trading with enhanced indicators
- **Risk Management**: Configurable position sizing, daily loss limits, and maximum trade limits
- **Trading Sessions**: Automatic trading during London and New York sessions
- **Dynamic TP/SL**: Take Profit and Stop Loss calculated based on ATR volatility
- **Comprehensive Logging**: Detailed trade logs and signal tracking
- **Backtesting Engine**: Historical performance analysis with detailed reports
- **Real-time Monitoring**: Live trading with continuous market analysis
- **Status Reporting**: Comprehensive bot status and performance metrics
- **Web Dashboard**: Real-time monitoring interface with charts and alerts

## Strategy Overview

The bot implements an enhanced scalping strategy with the following characteristics:

- **Timeframe**: 1-minute (M1) charts with 5-minute (M5) confirmation
- **Indicators**: 
  - EMA(5) & EMA(20) for trend detection (updated from EMA21)
  - RSI(14) for overbought/oversold conditions
  - ATR(14) for volatility-based position sizing
  - MACD for momentum confirmation
- **Risk Management**:
  - 0.5% - 1% risk per trade
  - Maximum 5 trades per day
  - Maximum 3% daily loss
  - Risk-Reward ratio: 1.5:1 minimum
  - Adaptive cooldown periods
- **Trading Conditions**:
  - Only during London (08:00-16:00 UTC) and New York (13:00-21:00 UTC) sessions
  - Multi-timeframe confirmation required
  - Minimum signal quality score of 60
  - Volatility and momentum filters active

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install MetaTrader 5**:
   - Download and install MetaTrader 5 from your broker
   - Ensure you have a demo or live account

3. **Configure Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   MT5_LOGIN=your_login_number
   MT5_PASSWORD=your_password
   MT5_SERVER=your_broker_server
   ```

## Configuration

Edit `config.py` to customize the bot parameters:

```python
CONFIG = {
    'risk_per_trade': 0.01,        # 1% risk per trade
    'max_trades_per_day': 5,       # Maximum trades per day
    'max_daily_loss': 0.03,        # 3% maximum daily loss
    'signal_minimum_score': 60,    # Minimum signal score to execute
    'cooldown_win_minutes': 3,     # Cooldown after winning trade
    'cooldown_loss_minutes': 10,   # Cooldown after losing trade
    'atr_sl_multiplier': 1.2,      # ATR multiplier for stop loss
    'atr_tp_multiplier': 1.8,      # ATR multiplier for take profit
    # ... more parameters
}
```

## Usage

### Live Trading

Run the bot for live trading:

```bash
python main.py
```

The bot will:
1. Connect to MetaTrader 5
2. Initialize all v3 components (MTF, cooldown, signal evaluator, etc.)
3. Start monitoring the market every minute
4. Execute trades based on enhanced strategy signals
5. Log all activities and trades with detailed analysis

### Real-Time Dashboard

Launch the monitoring dashboard:

```bash
streamlit run dashboard.py
```

The dashboard provides:
- **Live Market Data**: Current price, indicators, and signals
- **Performance Metrics**: P&L, win rate, account balance, drawdown
- **Alerts & Warnings**: Daily loss limits, cooldown status, pause conditions
- **Trade History**: Recent trades with timestamps and results
- **Signal Analysis**: Quality breakdown and filter status
- **Interactive Charts**: Price charts with EMA indicators
- **Auto-Refresh**: Configurable refresh intervals

### Status Report

Get a comprehensive status report:

```bash
python main.py status
```

This shows:
- Risk management status
- Cooldown information
- Pause status
- Multi-timeframe indicators
- Market conditions

### Backtesting

Run backtesting to analyze historical performance:

```bash
python backtest.py
```

### Testing

Test all v3 components:

```bash
python test_bot_v3.py
```

## File Structure

```
xauusd_scalping_bot_v3/
├── main.py               # Entry point for live trading (V3)
├── backtest.py           # Backtesting engine
├── dashboard.py          # Real-time monitoring dashboard (NEW)
├── config.py             # Configuration settings (V3 enhanced)
├── indicators.py         # Technical indicators calculation (V3)
├── strategy.py           # Trading strategy logic (V3 enhanced)
├── risk_management.py    # Risk management and position sizing
├── trade_executor.py     # MT5 order execution
├── logger.py             # Logging and trade tracking
├── utils.py              # Helper functions
├── test_bot_v3.py        # V3 component testing (NEW)
├── requirements.txt      # Python dependencies (V3 enhanced)
├── README.md            # This file
├── modules/             # V3 enhancement modules (NEW)
│   ├── __init__.py      # Package initialization
│   ├── mtf_filter.py    # Multi-timeframe filter
│   ├── cooldown_manager.py   # Trade cooldown logic
│   ├── signal_evaluator.py   # Signal scoring system
│   ├── volatility_filter.py  # ATR and momentum filter
│   └── pause_manager.py      # Auto-pause and resume logic
└── reports/             # Backtest reports and logs
    ├── trade_log_v3.csv
    ├── signal_log_v3.csv
    └── backtest_report_*.html
```

## V3 Performance Metrics

The bot tracks and reports the following enhanced metrics:

- **Total Return**: Overall profit/loss percentage
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure
- **Signal Quality Score**: Average signal quality per trade
- **Multi-timeframe Alignment**: Percentage of trades with MTF confirmation
- **Cooldown Efficiency**: Impact of cooldown periods on performance
- **Volatility Filter Effectiveness**: Performance during high vs low volatility
- **Pause Mode Impact**: Performance during auto-pause periods

## Risk Warning

⚠️ **IMPORTANT**: This bot is for educational and research purposes. Trading forex involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

- Always test thoroughly on a demo account before live trading
- Monitor the bot's performance regularly
- Never risk more than you can afford to lose
- Consider market conditions and news events that may affect performance
- The v3 enhancements add complexity - ensure you understand all features

## V3 Customization

### Adjusting Signal Scoring

Edit `signal_evaluator.py` to modify scoring weights:

```python
# Modify scoring factors in calculate_signal_score method
if rsi_distance > 10:
    score += 10  # RSI distance points
```

### Modifying Cooldown Periods

Edit `config.py` to adjust cooldown times:

```python
'cooldown_win_minutes': 3,   # After winning trade
'cooldown_loss_minutes': 10, # After losing trade
```

### Customizing Volatility Filter

Edit `volatility_filter.py` to adjust volatility thresholds:

```python
self.min_volatility_ratio = 1.0  # Current ATR must be >= ATR MA
```

## Troubleshooting

### Common V3 Issues

1. **Low Signal Scores**:
   - Check market volatility conditions
   - Verify multi-timeframe alignment
   - Review RSI and momentum indicators

2. **Frequent Pauses**:
   - Market may be in low volatility period
   - Check consecutive NONE signal count
   - Review trading session times

3. **Cooldown Conflicts**:
   - Check last trade result
   - Verify cooldown timing
   - Review risk management settings

### Enhanced Logs

Check the following log files for debugging:
- `trading_bot_v3.log`: General bot activity with v3 enhancements
- `trade_log_v3.csv`: Detailed trade records
- `signal_log_v3.csv`: Strategy signals and quality scores

## Support

For issues and questions:
1. Check the logs for error messages
2. Review the configuration settings
3. Test with different parameters using `test_bot_v3.py`
4. Run backtests to validate strategy changes
5. Use status report to diagnose issues

## License

This project is for educational purposes. Use at your own risk.

## Disclaimer

This software is provided "as is" without warranty. The authors are not responsible for any financial losses incurred through the use of this bot. Always test thoroughly and trade responsibly.

## Further Help

For detailed setup, troubleshooting, and advanced usage, please refer to the full user manual in [MANUAL.md](./MANUAL.md). 