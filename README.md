# XAU/USD Scalping Bot v1.0

A sophisticated automated trading bot for XAU/USD (Gold) scalping with advanced features including multi-timeframe confirmation, adaptive cooldown, signal quality scoring, and comprehensive risk management.

## 🚀 Features

### Core Trading Features
- **Multi-timeframe Analysis**: M1 + M5 confirmation with EMA(5) & EMA(20)
- **Advanced Indicators**: EMA, RSI, ATR, MACD with optimized parameters
- **Dynamic SL/TP**: ATR-based stop loss and take profit levels
- **Risk Management**: Daily loss limits, trade limits, and position sizing

### Enhanced Features
- **Signal Quality Scoring**: Minimum score 60 required for trade execution
- **Volatility Filter**: ATR vs ATR MA comparison for market conditions
- **Momentum Filter**: MACD histogram analysis for trend strength
- **Adaptive Cooldown**: 3 min after win, 10 min after loss
- **Auto Pause**: Automatic pause after 3 consecutive NONE signals
- **Comprehensive Logging**: Detailed trade and signal logging

## 📋 Requirements

- Python 3.8+
- MetaTrader5 (Windows) or Mock API (macOS/Linux)
- MT5 broker account with API access

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd untitled
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install TA-Lib (Required for Technical Indicators)
```bash
# macOS
brew install ta-lib
pip install TA-Lib

# Windows
# Download and install from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# Then: pip install TA_Lib-0.4.24-cp39-cp39-win_amd64.whl

# Linux
sudo apt-get install ta-lib
pip install TA-Lib
```

## ⚙️ Configuration

### 1. Environment Setup
Copy the example environment file:
```bash
cp env_example.txt .env
```

### 2. Configure MT5 Settings
Edit `.env` with your MT5 credentials:
```env
# MT5 Connection Settings
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo

# Risk Management
MAX_DAILY_LOSS=100
MAX_DAILY_TRADES=10
RISK_PERCENT=2.0
POSITION_SIZE=0.1

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### 3. Platform-Specific Setup

#### Windows (MT5 Desktop)
- Install MetaTrader5 desktop application
- Configure your broker account
- The bot will use the native MT5 API

#### macOS/Linux (Mock API)
- The bot will automatically use the mock API
- Perfect for testing and development
- No MT5 installation required

## 🚀 Usage

### Live Trading
```bash
python main.py
```

### Backtesting
```bash
python backtest.py
```

### Test Imports
```bash
python test_imports.py
```

### Test Bot
```bash
python test_bot.py
```

## 📊 Strategy Overview

### Signal Generation
1. **Multi-timeframe Confirmation**: M1 and M5 EMA crossovers
2. **RSI Filter**: Oversold/overbought conditions
3. **ATR Analysis**: Volatility measurement
4. **MACD Momentum**: Trend strength confirmation

### Risk Management
- **Daily Loss Limit**: Configurable maximum daily loss
- **Trade Limits**: Maximum trades per day
- **Position Sizing**: Risk-based position calculation
- **Dynamic SL/TP**: ATR-based stop loss and take profit

### Advanced Filters
- **Signal Quality**: Minimum score requirement
- **Volatility Filter**: Market condition assessment
- **Momentum Filter**: Trend strength validation
- **Cooldown Management**: Adaptive trade timing

## 📁 Project Structure

```
untitled/
├── main.py                 # Main bot entry point
├── config.py              # Configuration settings
├── strategy.py            # Trading strategy logic
├── indicators.py          # Technical indicators
├── risk_management.py     # Risk management
├── trade_executor.py      # Trade execution
├── api_manager.py         # MT5 API management
├── mock_mt5.py           # Mock API for testing
├── logger.py             # Logging utilities
├── backtest.py           # Backtesting module
├── utils.py              # Utility functions
├── modules/              # Enhanced modules
│   ├── mtf_filter.py     # Multi-timeframe filter
│   ├── cooldown_manager.py # Adaptive cooldown
│   ├── signal_evaluator.py # Signal quality scoring
│   ├── volatility_filter.py # Volatility analysis
│   └── pause_manager.py  # Auto-pause functionality
├── reports/              # Generated reports
├── requirements.txt      # Python dependencies
└── .env                 # Environment variables
```

## 🔧 Configuration Options

### Trading Parameters
- `SYMBOL`: Trading symbol (default: XAUUSD)
- `TIMEFRAME`: Primary timeframe (default: M1)
- `SECONDARY_TIMEFRAME`: Secondary timeframe (default: M5)

### Indicator Settings
- `EMA_FAST`: Fast EMA period (default: 5)
- `EMA_SLOW`: Slow EMA period (default: 21)
- `RSI_PERIOD`: RSI period (default: 14)
- `ATR_PERIOD`: ATR period (default: 14)

### Risk Management
- `MAX_DAILY_LOSS`: Maximum daily loss in USD
- `MAX_DAILY_TRADES`: Maximum trades per day
- `RISK_PERCENT`: Risk per trade percentage
- `POSITION_SIZE`: Default position size

### Advanced Settings
- `MIN_SIGNAL_SCORE`: Minimum signal quality score
- `COOLDOWN_WIN_MINUTES`: Cooldown after winning trade
- `COOLDOWN_LOSS_MINUTES`: Cooldown after losing trade
- `MAX_CONSECUTIVE_NONE`: Auto-pause threshold

## 📈 Performance Tracking

The bot generates comprehensive logs and reports:

- **Trade Log**: Detailed trade execution records
- **Signal Log**: Signal generation and analysis
- **Performance Metrics**: Win rate, profit factor, drawdown
- **Risk Metrics**: Daily P&L, position exposure

## 🛡️ Safety Features

- **Emergency Stop**: Immediate shutdown capability
- **Loss Limits**: Automatic stop on daily loss limit
- **Position Limits**: Maximum position restrictions
- **Error Handling**: Comprehensive error recovery
- **Logging**: Complete audit trail

## 🔍 Monitoring

### Log Files
- `trading_bot_v1.log`: Main application log
- `trade_log_v1.csv`: Trade execution records
- `signal_log_v1.csv`: Signal analysis records

### Real-time Monitoring
- Signal generation status
- Risk management status
- API connection status
- Performance metrics

## 🚨 Important Notes

### Risk Disclaimer
- This bot is for educational purposes
- Past performance doesn't guarantee future results
- Always test thoroughly before live trading
- Use proper risk management

### Platform Limitations
- **Windows**: Full MT5 API support
- **macOS/Linux**: Mock API for testing only
- For live trading on macOS/Linux, consider using a Windows VM or cloud server

### Broker Requirements
- MT5 broker account with API access
- Sufficient margin for position sizing
- Low latency connection recommended

## 🆘 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Install TA-Lib
brew install ta-lib  # macOS
pip install TA-Lib
```

#### MT5 Connection Issues
- Verify broker credentials
- Check MT5 server status
- Ensure API trading is enabled
- Contact broker support

#### Performance Issues
- Check system resources
- Optimize timeframe settings
- Review risk management parameters
- Monitor network latency

### Debug Mode
Enable debug logging in `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📞 Support

For issues and questions:
1. Check the logs in `trading_bot_v1.log`
2. Review configuration settings
3. Test with mock API first
4. Contact broker for API issues

## 📝 License

This project is for educational purposes. Use at your own risk.

## 🔄 Version History

### v1.0 (Current) - Initial Release
- Multi-timeframe confirmation
- Signal quality scoring
- Advanced filters
- Auto-pause functionality
- Enhanced risk management
- **Status**: Pre-launch, in development

### Planned Future Versions
- **v2.0**: Performance dashboard, advanced analytics
- **v3.0**: Machine learning integration, portfolio management 