# XAU/USD Scalping Bot V3 – User Manual

## 1. Introduction

Welcome to the XAU/USD Scalping Bot V3! This bot is designed for professional and hobbyist traders who want to automate gold (XAU/USD) scalping using MetaTrader 5 and Python. It features advanced risk management, multi-timeframe analysis, adaptive filters, and a real-time monitoring dashboard.

**Key Features:**
- Multi-timeframe trend confirmation (M1 + M5)
- Adaptive cooldowns after wins/losses
- ATR-based dynamic stop-loss/take-profit
- Signal quality scoring and filtering
- Volatility and momentum filters
- Auto-pause in flat/uncertain markets
- Real-time dashboard (Streamlit)
- Modular, testable codebase

## 2. System Requirements

- **Operating System:**
  - Windows (recommended for MetaTrader5 live trading)
  - macOS/Linux (for backtesting, dashboard, and logic testing; MetaTrader5 not supported natively)
- **Python:** 3.8–3.11 (recommended)
- **MetaTrader5:** Installed and configured (Windows only)
- **Other dependencies:** See `requirements.txt`

## 3. Installation

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd <repo-directory>
```

### Step 2: Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: On macOS/Linux, MetaTrader5 will not install. You can still use all logic, dashboard, and backtesting features.*

### Step 4: Install MetaTrader5 (Windows Only)
- Download MetaTrader5 from your broker or [MetaQuotes](https://www.metatrader5.com/en/download)
- Log in with your broker credentials

### Step 5: Configure Environment Variables
Create a `.env` file in the project root:
```
MT5_LOGIN=your_login_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

## 4. Configuration

Edit `config.py` to customize your trading parameters:
```python
CONFIG = {
    'symbol': 'XAUUSD',
    'timeframe': 'M1',
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
- **Risk Settings:** Adjust `risk_per_trade`, `max_trades_per_day`, and `max_daily_loss` to fit your risk profile.
- **Strategy Tweaks:** Change signal scoring, cooldowns, or indicator settings as needed.

## 5. Running the Bot

### Live Trading (Windows + MetaTrader5 only)
```bash
python main.py
```
- The bot will connect to MT5, initialize all modules, and start trading during active sessions.

### Backtesting
```bash
python backtest.py
```
- Analyze historical performance and generate reports in the `reports/` directory.

### Testing All Components
```bash
python test_bot_v3.py
```
- Runs unit tests for all v3 modules and logic.

### Import/Config Test
```bash
python test_imports.py
```
- Verifies that all modules and configuration load correctly.

## 6. Using the Dashboard

### Launch the Dashboard
```bash
streamlit run dashboard.py
```
- Opens a web dashboard in your browser.

### Dashboard Features
- **Live Market Data:** Price, indicators, and signals
- **Performance Metrics:** P&L, win rate, account stats
- **Alerts & Warnings:** Daily loss, cooldown, pause status
- **Trade/Signal History:** Recent trades and signal scores
- **Charts:** Price with EMA overlays
- **Auto-Refresh:** Set refresh interval (1–30 seconds)
- **Mode Switching:** Live/Backtest

### Interpreting the Dashboard
- **Green/Red/Gray signals:** BUY/SELL/NONE
- **Alerts:** Shown for risk, pause, or cooldown events
- **Performance:** Track your trading stats in real time

## 7. File Structure Overview

```
project_root/
├── main.py               # Live trading entry point
├── backtest.py           # Backtesting engine
├── dashboard.py          # Real-time dashboard
├── config.py             # Strategy parameters
├── indicators.py         # Indicator calculations
├── strategy.py           # Signal logic
├── risk_management.py    # Position sizing, SL/TP
├── trade_executor.py     # MT5 order interface
├── logger.py             # Logging
├── utils.py              # Helpers
├── test_bot_v3.py        # V3 tests
├── test_imports.py       # Import/config test
├── requirements.txt      # Dependencies
├── MANUAL.md             # This manual
├── modules/              # V3 modules
│   ├── __init__.py
│   ├── mtf_filter.py
│   ├── cooldown_manager.py
│   ├── signal_evaluator.py
│   ├── volatility_filter.py
│   └── pause_manager.py
└── reports/              # Backtest/trade logs
```

## 8. Troubleshooting

- **MetaTrader5 not installing:** Only supported on Windows. For macOS/Linux, use backtesting and dashboard only.
- **Dependency errors:** Ensure you're using a virtual environment and correct Python version.
- **No trades executed:** Check your config, market hours, and that your MT5 account is funded and logged in.
- **Dashboard not loading:** Make sure Streamlit is installed and run from the project root.
- **Permission errors:** Run terminal/IDE as administrator if needed.

## 9. FAQ

**Q: Can I run this bot on macOS or Linux?**
A: You can run all logic, backtesting, and the dashboard, but live trading via MetaTrader5 is only supported on Windows.

**Q: How do I change the risk per trade?**
A: Edit `risk_per_trade` in `config.py`.

**Q: Where are logs and reports saved?**
A: In the `reports/` directory.

**Q: How do I stop the bot?**
A: Press `Ctrl+C` in the terminal or stop the process in your IDE.

**Q: Can I use this bot for other symbols?**
A: Yes, but you must adjust the config and possibly the strategy logic for other instruments.

## 10. Support & Further Resources

- For technical details, see [README.md](./README.md)
- For MetaTrader5 Python API: [MetaTrader5 Docs](https://www.mql5.com/en/docs/integration/python_metatrader5)
- For Streamlit: [Streamlit Docs](https://docs.streamlit.io/)
- For help, open an issue in your project repository or contact the maintainer. 