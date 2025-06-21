import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from config import CONFIG
from indicators import calculate_indicators
from strategy import generate_signal, calculate_dynamic_tp_sl
from utils import get_historical_data_range, calculate_pips, calculate_profit_loss

class BacktestEngine:
    def __init__(self, start_date, end_date, initial_balance=10000):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity_curve = []
        self.trades = []
        self.current_position = None
        
    def load_data(self):
        """Load historical data for backtesting"""
        print(f"Loading data from {self.start_date} to {self.end_date}...")
        
        self.data = get_historical_data_range(
            CONFIG['symbol'], 
            CONFIG['timeframe'], 
            self.start_date, 
            self.end_date
        )
        
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data loaded for backtesting")
        
        print(f"Loaded {len(self.data)} data points")
        return self.data
    
    def calculate_indicators_for_data(self):
        """Calculate indicators for all data points"""
        print("Calculating indicators...")
        
        # Calculate EMAs
        self.data['ema5'] = self.data['close'].ewm(span=CONFIG['ema_fast']).mean()
        self.data['ema21'] = self.data['close'].ewm(span=CONFIG['ema_slow']).mean()
        
        # Calculate RSI
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=CONFIG['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=CONFIG['rsi_period']).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate ATR
        high_low = self.data['high'] - self.data['low']
        high_close = np.abs(self.data['high'] - self.data['close'].shift())
        low_close = np.abs(self.data['low'] - self.data['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.data['atr'] = tr.rolling(window=CONFIG['atr_period']).mean()
        
        print("Indicators calculated successfully")
    
    def simulate_trade(self, row, signal):
        """Simulate a trade execution"""
        if signal == "BUY":
            entry_price = row['close']
            volume = self.calculate_position_size()
            
            # Calculate TP/SL
            tp_price, sl_price = calculate_dynamic_tp_sl(row, signal, entry_price)
            
            self.current_position = {
                'type': 'BUY',
                'entry_time': row['time'],
                'entry_price': entry_price,
                'volume': volume,
                'tp_price': tp_price,
                'sl_price': sl_price,
                'atr': row['atr']
            }
            
        elif signal == "SELL":
            entry_price = row['close']
            volume = self.calculate_position_size()
            
            # Calculate TP/SL
            tp_price, sl_price = calculate_dynamic_tp_sl(row, signal, entry_price)
            
            self.current_position = {
                'type': 'SELL',
                'entry_time': row['time'],
                'entry_price': entry_price,
                'volume': volume,
                'tp_price': tp_price,
                'sl_price': sl_price,
                'atr': row['atr']
            }
    
    def check_exit_conditions(self, row):
        """Check if current position should be closed"""
        if self.current_position is None:
            return False
        
        current_price = row['close']
        position = self.current_position
        
        # Check stop loss
        if position['type'] == 'BUY' and current_price <= position['sl_price']:
            return 'SL'
        elif position['type'] == 'SELL' and current_price >= position['sl_price']:
            return 'SL'
        
        # Check take profit
        if position['type'] == 'BUY' and current_price >= position['tp_price']:
            return 'TP'
        elif position['type'] == 'SELL' and current_price <= position['tp_price']:
            return 'TP'
        
        return False
    
    def close_position(self, row, exit_reason):
        """Close current position and calculate P&L"""
        if self.current_position is None:
            return
        
        position = self.current_position
        exit_price = row['close']
        exit_time = row['time']
        
        # Calculate P&L
        if position['type'] == 'BUY':
            pips = calculate_pips(position['entry_price'], exit_price, True)
            profit = calculate_profit_loss(position['entry_price'], exit_price, position['volume'], True)
        else:  # SELL
            pips = calculate_pips(position['entry_price'], exit_price, False)
            profit = calculate_profit_loss(position['entry_price'], exit_price, position['volume'], False)
        
        # Apply commission
        commission = CONFIG['commission_per_lot'] * position['volume']
        net_profit = profit - commission
        
        # Update balance
        self.balance += net_profit
        
        # Record trade
        trade = {
            'entry_time': position['entry_time'],
            'exit_time': exit_time,
            'type': position['type'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'volume': position['volume'],
            'pips': pips,
            'profit': profit,
            'commission': commission,
            'net_profit': net_profit,
            'exit_reason': exit_reason,
            'balance': self.balance
        }
        
        self.trades.append(trade)
        self.current_position = None
    
    def calculate_position_size(self):
        """Calculate position size based on risk management"""
        risk_amount = self.balance * CONFIG['risk_per_trade']
        # Simplified calculation - in real implementation, use proper pip value
        position_size = risk_amount / 100  # Approximate for XAUUSD
        return max(0.01, round(position_size, 2))
    
    def run_backtest(self):
        """Run the complete backtest"""
        print("Starting backtest...")
        
        # Load and prepare data
        self.load_data()
        self.calculate_indicators_for_data()
        
        # Initialize tracking variables
        daily_trades = 0
        daily_pnl = 0
        last_date = None
        
        # Iterate through data
        for index, row in self.data.iterrows():
            # Skip rows with NaN indicators
            if pd.isna(row['ema5']) or pd.isna(row['ema21']) or pd.isna(row['rsi']) or pd.isna(row['atr']):
                continue
            
            # Check for position exit
            if self.current_position is not None:
                exit_reason = self.check_exit_conditions(row)
                if exit_reason:
                    self.close_position(row, exit_reason)
            
            # Check daily limits
            current_date = row['time'].date()
            if last_date != current_date:
                daily_trades = 0
                daily_pnl = 0
                last_date = current_date
            
            # Check if we can trade
            if (daily_trades >= CONFIG['max_trades_per_day'] or 
                daily_pnl <= -CONFIG['max_daily_loss'] * self.initial_balance):
                continue
            
            # Generate signal
            indicators = {
                'ema5': row['ema5'],
                'ema21': row['ema21'],
                'rsi': row['rsi'],
                'atr': row['atr']
            }
            
            signal = generate_signal(indicators)
            
            # Execute trade if no current position
            if signal != "NONE" and self.current_position is None:
                self.simulate_trade(row, signal)
                daily_trades += 1
            
            # Record equity
            current_equity = self.balance
            if self.current_position is not None:
                # Add unrealized P&L
                if self.current_position['type'] == 'BUY':
                    unrealized_pnl = (row['close'] - self.current_position['entry_price']) * self.current_position['volume'] * 100
                else:
                    unrealized_pnl = (self.current_position['entry_price'] - row['close']) * self.current_position['volume'] * 100
                current_equity += unrealized_pnl
            
            self.equity_curve.append({
                'time': row['time'],
                'equity': current_equity,
                'balance': self.balance
            })
        
        # Close any remaining position
        if self.current_position is not None:
            last_row = self.data.iloc[-1]
            self.close_position(last_row, 'END_OF_DATA')
        
        print("Backtest completed")
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive backtest report"""
        if not self.trades:
            return "No trades executed during backtest period"
        
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)
        
        # Calculate metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['net_profit'] > 0])
        losing_trades = len(trades_df[trades_df['net_profit'] < 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        total_profit = trades_df['net_profit'].sum()
        total_commission = trades_df['commission'].sum()
        
        # Calculate drawdown
        equity_df['peak'] = equity_df['equity'].expanding().max()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min()
        
        # Calculate Sharpe ratio (simplified)
        returns = equity_df['equity'].pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Profit factor
        gross_profit = trades_df[trades_df['net_profit'] > 0]['net_profit'].sum()
        gross_loss = abs(trades_df[trades_df['net_profit'] < 0]['net_profit'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Create report
        report = {
            'summary': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'initial_balance': self.initial_balance,
                'final_balance': self.balance,
                'total_return': (self.balance - self.initial_balance) / self.initial_balance * 100,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate * 100,
                'total_profit': total_profit,
                'total_commission': total_commission,
                'max_drawdown': max_drawdown * 100,
                'sharpe_ratio': sharpe_ratio,
                'profit_factor': profit_factor
            },
            'trades': trades_df,
            'equity_curve': equity_df
        }
        
        return report
    
    def save_report(self, report, filename=None):
        """Save backtest report to file"""
        if filename is None:
            filename = f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Create reports directory if it doesn't exist
        os.makedirs('reports', exist_ok=True)
        filepath = os.path.join('reports', filename)
        
        # Create HTML report
        html_content = self.create_html_report(report)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        print(f"Report saved to: {filepath}")
        return filepath
    
    def create_html_report(self, report):
        """Create HTML report with charts"""
        summary = report['summary']
        trades_df = report['trades']
        equity_df = report['equity_curve']
        
        # Create equity curve chart
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=equity_df['time'],
            y=equity_df['equity'],
            mode='lines',
            name='Equity Curve',
            line=dict(color='blue')
        ))
        fig_equity.update_layout(
            title='Equity Curve',
            xaxis_title='Time',
            yaxis_title='Equity ($)',
            height=400
        )
        
        # Create drawdown chart
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=equity_df['time'],
            y=equity_df['drawdown'] * 100,
            mode='lines',
            name='Drawdown (%)',
            line=dict(color='red'),
            fill='tonexty'
        ))
        fig_dd.update_layout(
            title='Drawdown',
            xaxis_title='Time',
            yaxis_title='Drawdown (%)',
            height=400
        )
        
        # Create trade distribution chart
        fig_trades = px.histogram(
            trades_df, 
            x='net_profit', 
            nbins=20,
            title='Trade Profit Distribution'
        )
        fig_trades.update_layout(height=400)
        
        # Generate HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>XAU/USD Scalping Bot Backtest Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>XAU/USD Scalping Bot Backtest Report</h1>
            <h2>Summary</h2>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><td>Period</td><td>{summary['start_date']} to {summary['end_date']}</td></tr>
                <tr><td>Initial Balance</td><td>${summary['initial_balance']:,.2f}</td></tr>
                <tr><td>Final Balance</td><td>${summary['final_balance']:,.2f}</td></tr>
                <tr><td>Total Return</td><td>{summary['total_return']:.2f}%</td></tr>
                <tr><td>Total Trades</td><td>{summary['total_trades']}</td></tr>
                <tr><td>Win Rate</td><td>{summary['win_rate']:.2f}%</td></tr>
                <tr><td>Total Profit</td><td>${summary['total_profit']:,.2f}</td></tr>
                <tr><td>Total Commission</td><td>${summary['total_commission']:,.2f}</td></tr>
                <tr><td>Max Drawdown</td><td>{summary['max_drawdown']:.2f}%</td></tr>
                <tr><td>Sharpe Ratio</td><td>{summary['sharpe_ratio']:.2f}</td></tr>
                <tr><td>Profit Factor</td><td>{summary['profit_factor']:.2f}</td></tr>
            </table>
            
            <div id="equity_chart"></div>
            <div id="drawdown_chart"></div>
            <div id="trades_chart"></div>
            
            <script>
                {fig_equity.to_json()}
                {fig_dd.to_json()}
                {fig_trades.to_json()}
                
                Plotly.newPlot('equity_chart', fig_equity.data, fig_equity.layout);
                Plotly.newPlot('drawdown_chart', fig_dd.data, fig_dd.layout);
                Plotly.newPlot('trades_chart', fig_trades.data, fig_trades.layout);
            </script>
        </body>
        </html>
        """
        
        return html_content

def run_backtest(start_date=None, end_date=None, initial_balance=10000):
    """Run backtest with specified parameters"""
    if start_date is None:
        start_date = CONFIG['backtest_start_date']
    if end_date is None:
        end_date = CONFIG['backtest_end_date']
    
    engine = BacktestEngine(start_date, end_date, initial_balance)
    report = engine.run_backtest()
    
    # Save report
    engine.save_report(report)
    
    # Print summary
    summary = report['summary']
    print("\n=== Backtest Results ===")
    print(f"Period: {summary['start_date']} to {summary['end_date']}")
    print(f"Initial Balance: ${summary['initial_balance']:,.2f}")
    print(f"Final Balance: ${summary['final_balance']:,.2f}")
    print(f"Total Return: {summary['total_return']:.2f}%")
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Win Rate: {summary['win_rate']:.2f}%")
    print(f"Max Drawdown: {summary['max_drawdown']:.2f}%")
    print(f"Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
    print(f"Profit Factor: {summary['profit_factor']:.2f}")
    print("=======================\n")
    
    return report

if __name__ == "__main__":
    run_backtest() 