import pandas as pd
import numpy as np
from config import CONFIG
from indicators import calculate_atr

class VolatilityFilter:
    def __init__(self):
        self.atr_period = 14
        self.atr_ma_period = 20
        self.min_volatility_ratio = 1.0  # Current ATR must be >= ATR MA
        
    def calculate_macd_histogram(self, close_prices, fast=12, slow=26, signal=9):
        """
        Calculate MACD histogram for momentum confirmation
        """
        if len(close_prices) < slow + signal:
            return None
        
        # Calculate EMAs
        ema_fast = close_prices.ewm(span=fast).mean()
        ema_slow = close_prices.ewm(span=slow).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=signal).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return histogram
    
    def check_volatility_conditions(self, data):
        """
        Check if current volatility is suitable for trading
        Returns: (suitable, reason, metrics)
        """
        if data is None or len(data) < self.atr_ma_period:
            return False, "Insufficient data", {}
        
        # Calculate ATR and its moving average
        data['atr'] = calculate_atr(data['high'], data['low'], data['close'], self.atr_period)
        data['atr_ma'] = data['atr'].rolling(window=self.atr_ma_period).mean()
        
        # Get latest values
        current_atr = data['atr'].iloc[-1]
        atr_ma = data['atr_ma'].iloc[-1]
        
        if pd.isna(current_atr) or pd.isna(atr_ma):
            return False, "ATR calculation failed", {}
        
        # Check if current ATR is above its moving average
        volatility_ratio = current_atr / atr_ma if atr_ma > 0 else 0
        
        metrics = {
            'current_atr': current_atr,
            'atr_ma': atr_ma,
            'volatility_ratio': volatility_ratio,
            'min_required_ratio': self.min_volatility_ratio
        }
        
        if volatility_ratio < self.min_volatility_ratio:
            return False, f"Low volatility (ratio: {volatility_ratio:.2f})", metrics
        
        return True, "Volatility conditions met", metrics
    
    def check_momentum_conditions(self, data):
        """
        Check momentum conditions using MACD histogram
        Returns: (suitable, reason, metrics)
        """
        if data is None or len(data) < 50:  # Need enough data for MACD
            return False, "Insufficient data for momentum analysis", {}
        
        # Calculate MACD histogram
        histogram = self.calculate_macd_histogram(data['close'])
        
        if histogram is None:
            return False, "MACD calculation failed", {}
        
        # Get recent histogram values
        current_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2] if len(histogram) > 1 else 0
        
        # Check for momentum
        momentum_positive = current_hist > 0
        momentum_increasing = current_hist > prev_hist
        
        metrics = {
            'current_histogram': current_hist,
            'previous_histogram': prev_hist,
            'momentum_positive': momentum_positive,
            'momentum_increasing': momentum_increasing
        }
        
        # Momentum is good if histogram is positive and increasing
        if momentum_positive and momentum_increasing:
            return True, "Strong positive momentum", metrics
        elif momentum_positive:
            return True, "Positive momentum", metrics
        else:
            return False, "Weak or negative momentum", metrics
    
    def get_volatility_status(self, data):
        """
        Get comprehensive volatility and momentum status
        """
        volatility_ok, vol_reason, vol_metrics = self.check_volatility_conditions(data)
        momentum_ok, mom_reason, mom_metrics = self.check_momentum_conditions(data)
        
        status = {
            'volatility_suitable': volatility_ok,
            'volatility_reason': vol_reason,
            'volatility_metrics': vol_metrics,
            'momentum_suitable': momentum_ok,
            'momentum_reason': mom_reason,
            'momentum_metrics': mom_metrics,
            'overall_suitable': volatility_ok and momentum_ok
        }
        
        return status
    
    def should_skip_trading(self, data):
        """
        Determine if trading should be skipped due to volatility/momentum conditions
        """
        status = self.get_volatility_status(data)
        return not status['overall_suitable'], status
    
    def get_volatility_score(self, data):
        """
        Calculate a volatility score (0-100) for signal evaluation
        """
        if data is None or len(data) < self.atr_ma_period:
            return 0
        
        # Calculate ATR metrics
        data['atr'] = calculate_atr(data['high'], data['low'], data['close'], self.atr_period)
        data['atr_ma'] = data['atr'].rolling(window=self.atr_ma_period).mean()
        
        current_atr = data['atr'].iloc[-1]
        atr_ma = data['atr_ma'].iloc[-1]
        
        if pd.isna(current_atr) or pd.isna(atr_ma) or atr_ma == 0:
            return 0
        
        # Calculate volatility ratio
        volatility_ratio = current_atr / atr_ma
        
        # Score based on volatility ratio
        if volatility_ratio >= 1.5:
            score = 100  # High volatility
        elif volatility_ratio >= 1.2:
            score = 80   # Good volatility
        elif volatility_ratio >= 1.0:
            score = 60   # Acceptable volatility
        elif volatility_ratio >= 0.8:
            score = 30   # Low volatility
        else:
            score = 0    # Very low volatility
        
        return score
    
    def get_momentum_score(self, data):
        """
        Calculate a momentum score (0-100) for signal evaluation
        """
        if data is None or len(data) < 50:
            return 0
        
        histogram = self.calculate_macd_histogram(data['close'])
        
        if histogram is None:
            return 0
        
        # Get recent histogram values
        current_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2] if len(histogram) > 1 else 0
        
        # Calculate momentum score
        if current_hist > 0 and current_hist > prev_hist:
            score = 100  # Strong positive momentum
        elif current_hist > 0:
            score = 70   # Positive momentum
        elif current_hist > prev_hist:
            score = 40   # Improving momentum
        else:
            score = 0    # Weak momentum
        
        return score

# Global instance
volatility_filter = VolatilityFilter() 