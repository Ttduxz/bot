import time
import schedule
from datetime import datetime
from config import CONFIG
from strategy import generate_signal, get_comprehensive_signal_analysis, update_indicators_for_v3
from trade_executor import initialize_mt5, place_order, check_max_positions
from indicators import calculate_indicators
from risk_management import risk_manager, can_trade
from logger import log_trade, log_signal, log_info, log_error, initialize_logs
from utils import get_historical_data, print_account_summary, is_market_open, wait_for_next_minute
from modules.mtf_filter import mtf_filter
from modules.cooldown_manager import cooldown_manager
from modules.signal_evaluator import signal_evaluator
from modules.volatility_filter import volatility_filter
from modules.pause_manager import pause_manager

class XAUUSDScalpingBotV3:
    def __init__(self):
        self.is_running = False
        self.last_signal = None
        self.session_started = False
        
    def initialize(self):
        """Initialize the trading bot (Enhanced for v3)"""
        log_info("Initializing XAU/USD Scalping Bot V3...")
        
        # Initialize MT5 connection
        if not initialize_mt5():
            log_error("Failed to initialize MT5 connection")
            return False
        
        # Initialize log files
        initialize_logs()
        
        # Initialize multi-timeframe filter
        mtf_success, mtf_message = mtf_filter.get_multi_timeframe_data(CONFIG['symbol'])
        if not mtf_success:
            log_warning(f"MTF initialization warning: {mtf_message}")
        
        # Start trading session
        pause_manager.start_session()
        self.session_started = True
        
        # Print account summary
        print_account_summary()
        
        log_info("Bot V3 initialized successfully")
        return True
    
    def check_trading_conditions(self):
        """Check if all trading conditions are met (Enhanced for v3)"""
        # Check if market is open
        if not is_market_open():
            return False, "Market is closed (weekend)"
        
        # Check risk management conditions
        can_trade_flag, message = can_trade()
        if not can_trade_flag:
            return False, message
        
        # Check cooldown conditions
        if not cooldown_manager.can_trade():
            remaining = cooldown_manager.get_cooldown_remaining()
            return False, f"In cooldown period ({remaining} minutes remaining)"
        
        # Check position limits
        if not check_max_positions():
            return False, "Maximum positions reached"
        
        # Check pause manager conditions
        can_trade_pause, pause_reason = pause_manager.can_trade()
        if not can_trade_pause:
            return False, pause_reason
        
        return True, "All conditions met"
    
    def execute_trading_cycle(self):
        """Execute one complete trading cycle (Enhanced for v3)"""
        try:
            # Check trading conditions
            conditions_ok, message = self.check_trading_conditions()
            if not conditions_ok:
                log_info(f"Trading conditions not met: {message}")
                return
            
            # Get recent price data
            rates = get_historical_data(CONFIG['symbol'], CONFIG['timeframe'], 100)
            if rates is None:
                log_error("Failed to get price data")
                return
            
            # Update indicators for v3
            rates = update_indicators_for_v3(rates)
            
            # Calculate indicators
            indicators = calculate_indicators(rates)
            
            # Get comprehensive signal analysis
            analysis = get_comprehensive_signal_analysis(indicators, rates)
            signal = analysis['signal']
            
            # Auto-manage pause based on signal
            pause_manager.auto_manage_pause(signal)
            
            # Log signal with enhanced information
            log_signal(signal, indicators)
            log_info(f"Signal Analysis: {analysis['signal_analysis']['quality']} (Score: {analysis['signal_analysis']['score']})")
            
            # Check if signal changed and is valid
            if signal != self.last_signal and signal != "NONE":
                log_info(f"New signal generated: {signal}")
                self.last_signal = signal
                
                # Calculate position size
                stop_loss_pips = CONFIG['stop_loss_pips']
                position_size = risk_manager.calculate_position_size(
                    CONFIG['risk_per_trade'], 
                    stop_loss_pips
                )
                
                # Place order
                order_result = place_order(
                    CONFIG['symbol'], 
                    signal, 
                    position_size, 
                    indicators
                )
                
                # Log trade result
                log_trade(order_result)
                
                # Update risk manager
                if order_result:
                    risk_manager.update_daily_stats(order_result)
                    
                    if order_result.retcode == 10009:  # Order placed successfully
                        log_info(f"Order placed successfully: {signal} {position_size} lots")
                        
                        # Record trade for cooldown management
                        # Note: We'll need to update this when we know the trade result
                        cooldown_manager.record_trade_result("UNKNOWN")
                        pause_manager.record_trade()
                    else:
                        log_error(f"Order failed with code: {order_result.retcode}")
            
        except Exception as e:
            log_error(f"Error in trading cycle: {str(e)}")
    
    def run_continuous(self):
        """Run the bot continuously (Enhanced for v3)"""
        log_info("Starting continuous trading mode (V3)...")
        self.is_running = True
        
        while self.is_running:
            try:
                self.execute_trading_cycle()
                
                # Wait for next minute
                wait_for_next_minute()
                
            except KeyboardInterrupt:
                log_info("Bot stopped by user")
                self.is_running = False
                break
            except Exception as e:
                log_error(f"Unexpected error: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        # End session when stopping
        if self.session_started:
            pause_manager.end_session()
    
    def run_scheduled(self):
        """Run the bot on a schedule (Enhanced for v3)"""
        log_info("Starting scheduled trading mode (V3)...")
        
        # Schedule trading cycle every minute
        schedule.every().minute.do(self.execute_trading_cycle)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                log_info("Bot stopped by user")
                break
            except Exception as e:
                log_error(f"Unexpected error: {str(e)}")
                time.sleep(60)
        
        # End session when stopping
        if self.session_started:
            pause_manager.end_session()
    
    def stop(self):
        """Stop the bot"""
        log_info("Stopping bot...")
        self.is_running = False
        
        if self.session_started:
            pause_manager.end_session()
    
    def get_status_report(self):
        """Get comprehensive status report (New for v3)"""
        # Get risk management status
        risk_stats = risk_manager.get_daily_stats()
        
        # Get cooldown status
        cooldown_status = cooldown_manager.get_cooldown_status()
        
        # Get pause status
        pause_status = pause_manager.get_status()
        
        # Get MTF status
        mtf_indicators = mtf_filter.get_mtf_indicators()
        
        status_report = {
            'timestamp': datetime.now(),
            'bot_running': self.is_running,
            'session_started': self.session_started,
            'risk_management': risk_stats,
            'cooldown_status': cooldown_status,
            'pause_status': pause_status,
            'mtf_indicators': mtf_indicators,
            'market_open': is_market_open(),
            'trading_session': self.is_in_trading_session()
        }
        
        return status_report
    
    def is_in_trading_session(self):
        """Check if currently in trading session"""
        from strategy import is_trading_session
        return is_trading_session()

def run_live_bot():
    """Main function to run the live trading bot (Enhanced for v3)"""
    bot = XAUUSDScalpingBotV3()
    
    # Initialize bot
    if not bot.initialize():
        log_error("Failed to initialize bot")
        return
    
    try:
        # Run in continuous mode
        bot.run_continuous()
    except Exception as e:
        log_error(f"Bot crashed: {str(e)}")
    finally:
        bot.stop()

def print_status_report():
    """Print a comprehensive status report (New for v3)"""
    bot = XAUUSDScalpingBotV3()
    
    if not bot.initialize():
        print("Failed to initialize bot for status report")
        return
    
    status = bot.get_status_report()
    
    print("\n" + "="*60)
    print("XAU/USD SCALPING BOT V3 - STATUS REPORT")
    print("="*60)
    
    print(f"Timestamp: {status['timestamp']}")
    print(f"Bot Running: {status['bot_running']}")
    print(f"Session Started: {status['session_started']}")
    print(f"Market Open: {status['market_open']}")
    print(f"Trading Session: {status['trading_session']}")
    
    print("\n--- Risk Management ---")
    risk = status['risk_management']
    print(f"Trades Today: {risk['trades_today']}")
    print(f"Daily PnL: ${risk['daily_pnl']:.2f}")
    print(f"Max Trades Remaining: {risk['max_trades_remaining']}")
    print(f"Max Loss Remaining: ${risk['max_loss_remaining']:.2f}")
    
    print("\n--- Cooldown Status ---")
    cooldown = status['cooldown_status']
    print(f"In Cooldown: {cooldown['in_cooldown']}")
    if cooldown['in_cooldown']:
        print(f"Remaining: {cooldown['remaining_minutes']} minutes")
    print(f"Last Trade Result: {cooldown['last_trade_result']}")
    
    print("\n--- Pause Status ---")
    pause = status['pause_status']
    print(f"Is Paused: {pause['is_paused']}")
    print(f"Consecutive NONE Signals: {pause['consecutive_none_signals']}")
    print(f"Session Active: {pause['session_active']}")
    
    print("\n--- Multi-Timeframe Status ---")
    mtf = status['mtf_indicators']
    if mtf:
        print(f"M1 EMA5: {mtf['m1_ema5']:.2f}")
        print(f"M1 EMA20: {mtf['m1_ema20']:.2f}")
        print(f"M5 EMA5: {mtf['m5_ema5']:.2f}")
        print(f"M5 EMA20: {mtf['m5_ema20']:.2f}")
    else:
        print("MTF data not available")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print_status_report()
    else:
        run_live_bot() 