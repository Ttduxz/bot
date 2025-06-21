#!/usr/bin/env python3
"""
Real-Time Monitoring Dashboard for XAU/USD Scalping Bot V3
Provides a web interface for monitoring bot activity, trade signals, 
performance statistics, and alerts during both backtesting and live trading sessions.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
import json
import os
from typing import Dict, List, Optional

# Import bot modules
from config import CONFIG
from indicators import calculate_indicators
from strategy import get_comprehensive_signal_analysis
from utils import get_historical_data, print_account_summary
from modules.mtf_filter import mtf_filter
from modules.cooldown_manager import cooldown_manager
from modules.signal_evaluator import signal_evaluator
from modules.volatility_filter import volatility_filter
from modules.pause_manager import pause_manager
from logger import log_info, log_error

class TradingDashboard:
    def __init__(self):
        self.is_running = False
        self.data_cache = {}
        self.trade_history = []
        self.signal_history = []
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_drawdown': 0.0
        }
        
    def initialize(self):
        """Initialize the dashboard"""
        st.set_page_config(
            page_title="XAU/USD Scalping Bot V3 Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state
        if 'dashboard_mode' not in st.session_state:
            st.session_state.dashboard_mode = 'Live'
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
        if 'refresh_interval' not in st.session_state:
            st.session_state.refresh_interval = 5
        
    def get_current_market_data(self):
        """Get current market data and indicators"""
        try:
            # Get recent price data
            rates = get_historical_data(CONFIG['symbol'], CONFIG['timeframe'], 100)
            if rates is None:
                return None
            
            # Calculate indicators
            indicators = calculate_indicators(rates)
            
            # Get comprehensive signal analysis
            analysis = get_comprehensive_signal_analysis(indicators, rates)
            
            return {
                'rates': rates,
                'indicators': indicators,
                'analysis': analysis,
                'timestamp': datetime.now()
            }
        except Exception as e:
            log_error(f"Error getting market data: {str(e)}")
            return None
    
    def get_account_metrics(self):
        """Get live account metrics"""
        try:
            # This would normally connect to MT5 to get real account data
            # For demo purposes, we'll return mock data
            return {
                'balance': 10000.0,
                'equity': 10150.0,
                'profit': 150.0,
                'drawdown_percent': 2.5,
                'open_positions': 1,
                'margin_level': 85.0
            }
        except Exception as e:
            log_error(f"Error getting account metrics: {str(e)}")
            return None
    
    def render_header(self):
        """Render dashboard header"""
        st.title("📈 XAU/USD Scalping Bot V3 - Real-Time Dashboard")
        
        # Mode selector and controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            mode = st.selectbox(
                "Mode",
                ["Live", "Backtest"],
                index=0 if st.session_state.dashboard_mode == 'Live' else 1
            )
            st.session_state.dashboard_mode = mode
        
        with col2:
            st.session_state.auto_refresh = st.checkbox(
                "Auto Refresh",
                value=st.session_state.auto_refresh
            )
        
        with col3:
            if st.session_state.auto_refresh:
                st.session_state.refresh_interval = st.selectbox(
                    "Refresh Interval (seconds)",
                    [1, 3, 5, 10, 30],
                    index=2
                )
        
        with col4:
            if st.button("🔄 Manual Refresh"):
                st.rerun()
        
        st.markdown("---")
    
    def render_market_data(self, market_data):
        """Render current market data section"""
        if market_data is None:
            st.error("❌ Unable to fetch market data")
            return
        
        indicators = market_data['indicators']
        analysis = market_data['analysis']
        
        st.subheader("📊 Current Market Data")
        
        # Create three columns for market data
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Price",
                f"${indicators['close']:.2f}",
                f"{indicators['close'] - indicators.get('prev_close', indicators['close']):.2f}"
            )
            
            st.metric(
                "ATR (14)",
                f"{indicators['atr']:.4f}",
                f"{indicators['atr'] - indicators.get('atr_ma', indicators['atr']):.4f}"
            )
        
        with col2:
            st.metric(
                "EMA(5)",
                f"${indicators['ema5']:.2f}",
                f"{indicators['ema5'] - indicators['ema20']:.2f}"
            )
            
            st.metric(
                "EMA(20)",
                f"${indicators['ema20']:.2f}",
                ""
            )
        
        with col3:
            st.metric(
                "RSI (14)",
                f"{indicators['rsi']:.1f}",
                f"{indicators['rsi'] - 50:.1f}"
            )
            
            # Signal status
            signal_color = {
                "BUY": "🟢",
                "SELL": "🔴", 
                "NONE": "⚪"
            }.get(analysis['signal'], "⚪")
            
            st.metric(
                "Current Signal",
                f"{signal_color} {analysis['signal']}",
                f"Score: {analysis['signal_analysis']['score']}"
            )
    
    def render_indicators_chart(self, market_data):
        """Render indicators chart"""
        if market_data is None:
            return
        
        rates = market_data['rates']
        indicators = market_data['indicators']
        
        st.subheader("📈 Price & Indicators Chart")
        
        # Create price chart with indicators
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=rates['time'],
            open=rates['open'],
            high=rates['high'],
            low=rates['low'],
            close=rates['close'],
            name="Price",
            increasing_line_color='#00ff00',
            decreasing_line_color='#ff0000'
        ))
        
        # Add EMA lines
        fig.add_trace(go.Scatter(
            x=rates['time'],
            y=rates['ema5'],
            mode='lines',
            name='EMA(5)',
            line=dict(color='blue', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=rates['time'],
            y=rates['ema20'],
            mode='lines',
            name='EMA(20)',
            line=dict(color='orange', width=1)
        ))
        
        fig.update_layout(
            title="XAU/USD Price with EMAs",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_signal_analysis(self, market_data):
        """Render signal analysis section"""
        if market_data is None:
            return
        
        analysis = market_data['analysis']
        
        st.subheader("🎯 Signal Analysis")
        
        # Signal quality breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Signal Quality Breakdown:**")
            breakdown = analysis['signal_analysis']['breakdown']
            for component, score in breakdown.items():
                st.write(f"• {component}: {score} points")
        
        with col2:
            st.write("**Filter Status:**")
            
            # MTF Status
            mtf_status = "✅ Aligned" if analysis['mtf_aligned'] else "❌ Not Aligned"
            st.write(f"• Multi-Timeframe: {mtf_status}")
            
            # Volatility Status
            vol_status = analysis.get('volatility_status', {})
            if vol_status:
                vol_ok = vol_status.get('volatility_ok', False)
                vol_status_text = "✅ OK" if vol_ok else "❌ Low Volatility"
                st.write(f"• Volatility: {vol_status_text}")
            
            # Pause Status
            pause_status = analysis.get('pause_status', {})
            if pause_status:
                can_trade = pause_status.get('can_trade', True)
                pause_status_text = "✅ Active" if can_trade else "⏸️ Paused"
                st.write(f"• Bot Status: {pause_status_text}")
    
    def render_performance_metrics(self):
        """Render performance metrics section"""
        st.subheader("📊 Performance Metrics")
        
        # Get account metrics
        account_metrics = self.get_account_metrics()
        
        if account_metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Account Balance",
                    f"${account_metrics['balance']:,.2f}",
                    f"{account_metrics['profit']:+.2f}"
                )
            
            with col2:
                st.metric(
                    "Equity",
                    f"${account_metrics['equity']:,.2f}",
                    f"{account_metrics['profit']:+.2f}"
                )
            
            with col3:
                st.metric(
                    "Drawdown",
                    f"{account_metrics['drawdown_percent']:.1f}%",
                    ""
                )
            
            with col4:
                st.metric(
                    "Open Positions",
                    account_metrics['open_positions'],
                    ""
                )
        
        # Performance summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Trading Statistics:**")
            st.write(f"• Total Trades: {self.performance_metrics['total_trades']}")
            st.write(f"• Win Rate: {self.performance_metrics['win_rate']:.1f}%")
            st.write(f"• Total P&L: ${self.performance_metrics['total_pnl']:,.2f}")
        
        with col2:
            st.write("**Risk Metrics:**")
            st.write(f"• Average Win: ${self.performance_metrics['avg_win']:,.2f}")
            st.write(f"• Average Loss: ${self.performance_metrics['avg_loss']:,.2f}")
            st.write(f"• Max Drawdown: ${self.performance_metrics['max_drawdown']:,.2f}")
    
    def render_alerts_and_warnings(self, market_data):
        """Render alerts and warnings section"""
        st.subheader("⚠️ Alerts & Warnings")
        
        alerts = []
        
        # Check for exceeded daily loss limit
        if self.performance_metrics['total_pnl'] < -CONFIG['daily_loss_limit']:
            alerts.append({
                'type': 'danger',
                'message': f"🚨 Daily loss limit exceeded! Current loss: ${abs(self.performance_metrics['total_pnl']):,.2f}"
            })
        
        # Check cooldown status
        if not cooldown_manager.can_trade():
            remaining = cooldown_manager.get_cooldown_remaining()
            alerts.append({
                'type': 'warning',
                'message': f"⏳ Cooldown period active: {remaining} minutes remaining"
            })
        
        # Check pause status
        can_trade, pause_reason = pause_manager.can_trade()
        if not can_trade:
            alerts.append({
                'type': 'warning',
                'message': f"⏸️ Auto-pause triggered: {pause_reason}"
            })
        
        # Check market conditions
        if market_data:
            analysis = market_data['analysis']
            if analysis['signal'] == "NONE":
                alerts.append({
                    'type': 'info',
                    'message': "ℹ️ No trading signal - waiting for better conditions"
                })
        
        # Display alerts
        if alerts:
            for alert in alerts:
                if alert['type'] == 'danger':
                    st.error(alert['message'])
                elif alert['type'] == 'warning':
                    st.warning(alert['message'])
                elif alert['type'] == 'info':
                    st.info(alert['message'])
        else:
            st.success("✅ All systems operational - no alerts")
    
    def render_trade_history(self):
        """Render trade history section"""
        st.subheader("📋 Recent Trades")
        
        if not self.trade_history:
            st.info("No trades recorded yet")
            return
        
        # Convert to DataFrame for display
        df = pd.DataFrame(self.trade_history[-10:])  # Show last 10 trades
        
        if not df.empty:
            # Format the DataFrame
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['pnl'] = df['pnl'].apply(lambda x: f"${x:,.2f}")
            df['type'] = df['type'].apply(lambda x: f"{'🟢' if x == 'BUY' else '🔴'} {x}")
            
            st.dataframe(
                df[['timestamp', 'type', 'price', 'size', 'pnl', 'status']],
                use_container_width=True
            )
    
    def render_signal_history(self):
        """Render signal history section"""
        st.subheader("📡 Signal History")
        
        if not self.signal_history:
            st.info("No signals recorded yet")
            return
        
        # Convert to DataFrame for display
        df = pd.DataFrame(self.signal_history[-20:])  # Show last 20 signals
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['signal'] = df['signal'].apply(lambda x: f"{'🟢' if x == 'BUY' else '🔴' if x == 'SELL' else '⚪'} {x}")
            
            st.dataframe(
                df[['timestamp', 'signal', 'score', 'quality']],
                use_container_width=True
            )
    
    def run_dashboard(self):
        """Run the main dashboard"""
        self.initialize()
        
        # Render header
        self.render_header()
        
        # Get current market data
        market_data = self.get_current_market_data()
        
        # Create main layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Market data and charts
            self.render_market_data(market_data)
            self.render_indicators_chart(market_data)
            self.render_signal_analysis(market_data)
        
        with col2:
            # Performance and alerts
            self.render_performance_metrics()
            self.render_alerts_and_warnings(market_data)
        
        # Trade and signal history
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_trade_history()
        
        with col2:
            self.render_signal_history()
        
        # Auto-refresh functionality
        if st.session_state.auto_refresh:
            time.sleep(st.session_state.refresh_interval)
            st.rerun()

def main():
    """Main function to run the dashboard"""
    dashboard = TradingDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main() 