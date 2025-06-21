from datetime import datetime, timedelta
from config import CONFIG

class PauseManager:
    def __init__(self):
        self.consecutive_none_signals = 0
        self.last_trade_time = None
        self.pause_start_time = None
        self.pause_duration = timedelta(minutes=30)  # 30 minutes pause
        self.max_none_signals = 3  # Pause after 3 consecutive NONE signals
        self.session_start_time = None
        self.session_end_time = None
        
    def record_signal(self, signal):
        """
        Record a signal and update consecutive NONE count
        """
        if signal == "NONE":
            self.consecutive_none_signals += 1
        else:
            self.consecutive_none_signals = 0  # Reset counter on valid signal
    
    def record_trade(self):
        """
        Record when a trade is executed
        """
        self.last_trade_time = datetime.now()
        self.consecutive_none_signals = 0  # Reset counter on trade
    
    def check_auto_pause_conditions(self):
        """
        Check if auto-pause should be triggered
        Returns: (should_pause, reason)
        """
        # Check for consecutive NONE signals
        if self.consecutive_none_signals >= self.max_none_signals:
            return True, f"Auto-pause: {self.consecutive_none_signals} consecutive NONE signals"
        
        # Check if we're already in pause mode
        if self.is_paused():
            return True, "Currently in pause mode"
        
        return False, "No pause conditions met"
    
    def start_pause(self, reason="Manual pause"):
        """
        Start a pause period
        """
        self.pause_start_time = datetime.now()
        print(f"Pause started: {reason}")
    
    def end_pause(self):
        """
        End the current pause period
        """
        self.pause_start_time = None
        self.consecutive_none_signals = 0
        print("Pause ended")
    
    def is_paused(self):
        """
        Check if currently in pause mode
        """
        if self.pause_start_time is None:
            return False
        
        return datetime.now() < (self.pause_start_time + self.pause_duration)
    
    def get_pause_remaining(self):
        """
        Get remaining pause time in minutes
        """
        if not self.is_paused():
            return 0
        
        remaining = (self.pause_start_time + self.pause_duration) - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))
    
    def check_session_trading(self):
        """
        Check if we should deactivate for the day due to no trades
        """
        if self.session_start_time is None:
            return True, "Session not started"
        
        # Check if we're in a trading session
        from strategy import is_trading_session
        if not is_trading_session():
            return True, "Outside trading hours"
        
        # If no trades in current session, consider deactivating
        if self.last_trade_time is None or self.last_trade_time.date() < datetime.now().date():
            # No trades today
            return False, "No trades in current session"
        
        return True, "Session active"
    
    def start_session(self):
        """
        Start a new trading session
        """
        self.session_start_time = datetime.now()
        self.consecutive_none_signals = 0
        print(f"Trading session started at {self.session_start_time}")
    
    def end_session(self):
        """
        End the current trading session
        """
        self.session_end_time = datetime.now()
        print(f"Trading session ended at {self.session_end_time}")
        
        # Reset for next session
        self.session_start_time = None
        self.session_end_time = None
        self.consecutive_none_signals = 0
    
    def get_status(self):
        """
        Get comprehensive pause and session status
        """
        status = {
            'consecutive_none_signals': self.consecutive_none_signals,
            'max_none_signals': self.max_none_signals,
            'is_paused': self.is_paused(),
            'pause_remaining_minutes': self.get_pause_remaining(),
            'pause_start_time': self.pause_start_time,
            'last_trade_time': self.last_trade_time,
            'session_start_time': self.session_start_time,
            'session_end_time': self.session_end_time
        }
        
        # Add auto-pause check
        should_pause, pause_reason = self.check_auto_pause_conditions()
        status['should_pause'] = should_pause
        status['pause_reason'] = pause_reason
        
        # Add session status
        session_ok, session_reason = self.check_session_trading()
        status['session_active'] = session_ok
        status['session_reason'] = session_reason
        
        return status
    
    def can_trade(self):
        """
        Check if trading is allowed (not paused and session active)
        """
        # Check if paused
        if self.is_paused():
            return False, f"Paused for {self.get_pause_remaining()} more minutes"
        
        # Check auto-pause conditions
        should_pause, reason = self.check_auto_pause_conditions()
        if should_pause:
            return False, reason
        
        # Check session status
        session_ok, session_reason = self.check_session_trading()
        if not session_ok:
            return False, session_reason
        
        return True, "Trading allowed"
    
    def auto_manage_pause(self, signal):
        """
        Automatically manage pause based on signal
        """
        # Record the signal
        self.record_signal(signal)
        
        # Check if we should start a pause
        should_pause, reason = self.check_auto_pause_conditions()
        if should_pause and not self.is_paused():
            self.start_pause(reason)
            return False, reason
        
        # Check if pause should end
        if self.is_paused() and datetime.now() >= (self.pause_start_time + self.pause_duration):
            self.end_pause()
            return True, "Pause ended"
        
        return True, "No pause action needed"

# Global instance
pause_manager = PauseManager() 