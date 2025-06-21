import MetaTrader5 as mt5
import pandas as pd
from config import CONFIG
from indicators import calculate_ema
from utils import get_mt5_timeframe

class MultiTimeframeFilter:
    def __init__(self):
        self.m1_data = None
        self.m5_data = None
        
    def get_multi_timeframe_data(self, symbol, lookback=50):
        """
        Get data from both M1 and M5 timeframes
        """
        try:
            # Get M1 data
            m1_timeframe = get_mt5_timeframe('M1')
            m1_rates = mt5.copy_rates_from_pos(symbol, m1_timeframe, 0, lookback)
            
            # Get M5 data
            m5_timeframe = get_mt5_timeframe('M5')
            m5_rates = mt5.copy_rates_from_pos(symbol, m5_timeframe, 0, lookback)
            
            if m1_rates is None or m5_rates is None:
                return False, "Failed to get market data"
            
            # Convert to DataFrames
            self.m1_data = pd.DataFrame(m1_rates)
            self.m5_data = pd.DataFrame(m5_rates)
            
            # Calculate EMAs for both timeframes
            self.m1_data['ema5'] = calculate_ema(self.m1_data['close'], 5)
            self.m1_data['ema20'] = calculate_ema(self.m1_data['close'], 20)
            
            self.m5_data['ema5'] = calculate_ema(self.m5_data['close'], 5)
            self.m5_data['ema20'] = calculate_ema(self.m5_data['close'], 20)
            
            return True, "Data loaded successfully"
            
        except Exception as e:
            return False, f"Error loading multi-timeframe data: {str(e)}"
    
    def check_trend_alignment(self):
        """
        Check if M1 and M5 trends are aligned
        Returns: (aligned, trend_direction, confidence)
        """
        if self.m1_data is None or self.m5_data is None:
            return False, "NONE", 0
        
        # Get latest values
        m1_ema5 = self.m1_data['ema5'].iloc[-1]
        m1_ema20 = self.m1_data['ema20'].iloc[-1]
        m5_ema5 = self.m5_data['ema5'].iloc[-1]
        m5_ema20 = self.m5_data['ema20'].iloc[-1]
        
        # Check if data is valid
        if pd.isna(m1_ema5) or pd.isna(m1_ema20) or pd.isna(m5_ema5) or pd.isna(m5_ema20):
            return False, "NONE", 0
        
        # Check trend alignment
        m1_bullish = m1_ema5 > m1_ema20
        m5_bullish = m5_ema5 > m5_ema20
        
        if m1_bullish and m5_bullish:
            # Both timeframes show bullish trend
            confidence = self._calculate_trend_strength(self.m1_data, self.m5_data, "BULLISH")
            return True, "BULLISH", confidence
            
        elif not m1_bullish and not m5_bullish:
            # Both timeframes show bearish trend
            confidence = self._calculate_trend_strength(self.m1_data, self.m5_data, "BEARISH")
            return True, "BEARISH", confidence
        
        else:
            # Timeframes are not aligned
            return False, "NONE", 0
    
    def _calculate_trend_strength(self, m1_data, m5_data, trend_direction):
        """
        Calculate trend strength based on EMA separation
        """
        # M1 trend strength
        m1_ema_diff = abs(m1_data['ema5'].iloc[-1] - m1_data['ema20'].iloc[-1])
        m1_ema_ratio = m1_ema_diff / m1_data['close'].iloc[-1]
        
        # M5 trend strength
        m5_ema_diff = abs(m5_data['ema5'].iloc[-1] - m5_data['ema20'].iloc[-1])
        m5_ema_ratio = m5_ema_diff / m5_data['close'].iloc[-1]
        
        # Combine strengths (M5 has more weight as it's higher timeframe)
        total_strength = (m1_ema_ratio * 0.4) + (m5_ema_ratio * 0.6)
        
        # Convert to percentage (0-100)
        confidence = min(100, total_strength * 10000)  # Scale factor
        
        return confidence
    
    def get_mtf_signal(self):
        """
        Get multi-timeframe trading signal
        Returns: "BUY", "SELL", or "NONE"
        """
        aligned, trend, confidence = self.check_trend_alignment()
        
        if not aligned:
            return "NONE"
        
        # Only trade if confidence is above threshold
        if confidence < 30:  # Minimum confidence threshold
            return "NONE"
        
        if trend == "BULLISH":
            return "BUY"
        elif trend == "BEARISH":
            return "SELL"
        
        return "NONE"
    
    def get_mtf_indicators(self):
        """
        Get current indicators from both timeframes
        """
        if self.m1_data is None or self.m5_data is None:
            return None
        
        return {
            'm1_ema5': self.m1_data['ema5'].iloc[-1],
            'm1_ema20': self.m1_data['ema20'].iloc[-1],
            'm5_ema5': self.m5_data['ema5'].iloc[-1],
            'm5_ema20': self.m5_data['ema20'].iloc[-1],
            'm1_close': self.m1_data['close'].iloc[-1],
            'm5_close': self.m5_data['close'].iloc[-1]
        }

# Global instance
mtf_filter = MultiTimeframeFilter() 