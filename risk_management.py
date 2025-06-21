import MetaTrader5 as mt5
from datetime import datetime, date
from config import CONFIG

class RiskManager:
    def __init__(self):
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_trade_date = None
    
    def reset_daily_counters(self):
        """Reset daily counters if it's a new day"""
        today = date.today()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self.last_trade_date = today
    
    def can_trade(self):
        """Check if we can place a new trade based on daily limits"""
        self.reset_daily_counters()
        
        # Check max trades per day
        if self.daily_trades >= CONFIG['max_trades_per_day']:
            return False, "Max daily trades reached"
        
        # Check max daily loss
        if self.daily_pnl <= -CONFIG['max_daily_loss']:
            return False, "Max daily loss reached"
        
        return True, "OK"
    
    def calculate_position_size(self, risk_per_trade, stop_loss_pips):
        """
        Calculate position size based on risk percentage and stop loss
        """
        # Get account info
        account_info = mt5.account_info()
        if not account_info:
            return 0.01  # Default minimum lot size
        
        balance = account_info.balance
        risk_amount = balance * risk_per_trade
        
        # Get symbol info for pip value calculation
        symbol_info = mt5.symbol_info(CONFIG['symbol'])
        if not symbol_info:
            return 0.01
        
        # Calculate pip value (for XAUUSD, 1 pip = $0.1 per 0.01 lot)
        pip_value = 0.1  # USD per 0.01 lot per pip for XAUUSD
        
        # Calculate position size
        if stop_loss_pips > 0:
            position_size = risk_amount / (stop_loss_pips * pip_value * 100)
        else:
            position_size = 0.01
        
        # Round to 2 decimal places and ensure minimum size
        position_size = max(0.01, round(position_size, 2))
        
        return position_size
    
    def update_daily_stats(self, trade_result):
        """Update daily trading statistics"""
        self.reset_daily_counters()
        
        if trade_result.retcode == mt5.TRADE_RETCODE_DONE:
            self.daily_trades += 1
            # Note: PnL will be updated when position is closed
    
    def get_daily_stats(self):
        """Get current daily statistics"""
        self.reset_daily_counters()
        return {
            'trades_today': self.daily_trades,
            'daily_pnl': self.daily_pnl,
            'max_trades_remaining': CONFIG['max_trades_per_day'] - self.daily_trades,
            'max_loss_remaining': CONFIG['max_daily_loss'] + self.daily_pnl
        }

# Global risk manager instance
risk_manager = RiskManager()

def calculate_position_size(risk_per_trade, stop_loss_pips):
    """Wrapper function for backward compatibility"""
    return risk_manager.calculate_position_size(risk_per_trade, stop_loss_pips)

def can_trade():
    """Wrapper function for backward compatibility"""
    return risk_manager.can_trade() 