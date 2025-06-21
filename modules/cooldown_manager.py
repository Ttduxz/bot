from datetime import datetime, timedelta
from config import CONFIG

class CooldownManager:
    def __init__(self):
        self.last_trade_time = None
        self.last_trade_result = None  # "WIN", "LOSS", or None
        self.cooldown_end_time = None
        
    def record_trade_result(self, result):
        """
        Record the result of the last trade
        result: "WIN" or "LOSS"
        """
        self.last_trade_result = result
        self.last_trade_time = datetime.now()
        
        # Set cooldown based on trade result
        if result == "WIN":
            cooldown_minutes = 3  # Wait 3 candles after winning trade
        elif result == "LOSS":
            cooldown_minutes = 10  # Wait 10 candles after losing trade
        else:
            cooldown_minutes = 5  # Default cooldown
        
        self.cooldown_end_time = datetime.now() + timedelta(minutes=cooldown_minutes)
        
        print(f"Cooldown set for {cooldown_minutes} minutes after {result} trade")
    
    def is_in_cooldown(self):
        """
        Check if currently in cooldown period
        """
        if self.cooldown_end_time is None:
            return False
        
        return datetime.now() < self.cooldown_end_time
    
    def get_cooldown_remaining(self):
        """
        Get remaining cooldown time in minutes
        """
        if not self.is_in_cooldown():
            return 0
        
        remaining = self.cooldown_end_time - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))
    
    def get_cooldown_status(self):
        """
        Get detailed cooldown status
        """
        if not self.is_in_cooldown():
            return {
                'in_cooldown': False,
                'remaining_minutes': 0,
                'last_trade_result': self.last_trade_result,
                'last_trade_time': self.last_trade_time
            }
        
        return {
            'in_cooldown': True,
            'remaining_minutes': self.get_cooldown_remaining(),
            'last_trade_result': self.last_trade_result,
            'last_trade_time': self.last_trade_time,
            'cooldown_end_time': self.cooldown_end_time
        }
    
    def reset_cooldown(self):
        """
        Reset cooldown (useful for testing or manual override)
        """
        self.cooldown_end_time = None
        print("Cooldown reset")
    
    def can_trade(self):
        """
        Check if we can place a new trade
        """
        return not self.is_in_cooldown()

# Global instance
cooldown_manager = CooldownManager() 