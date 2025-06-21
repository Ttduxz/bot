import pandas as pd
import numpy as np
from config import CONFIG
from indicators import calculate_rsi, calculate_atr

class SignalEvaluator:
    def __init__(self):
        self.minimum_score = 60  # Minimum score required to execute trade
        
    def calculate_signal_score(self, indicators, mtf_aligned=False):
        """
        Calculate signal quality score based on multiple factors
        Returns score (0-100) and breakdown of points
        """
        score = 0
        breakdown = {}
        
        # 1. RSI Distance from 50 (+10 points if far from 50)
        rsi = indicators.get('rsi', 50)
        rsi_distance = abs(rsi - 50)
        if rsi_distance > 10:  # RSI above 60 or below 40
            score += 10
            breakdown['rsi_distance'] = 10
        else:
            breakdown['rsi_distance'] = 0
        
        # 2. ATR Volatility (+15 points if ATR > 20-period average)
        current_atr = indicators.get('atr', 0)
        atr_ma = indicators.get('atr_ma', 0)  # 20-period ATR average
        
        if atr_ma > 0 and current_atr > atr_ma:
            score += 15
            breakdown['atr_volatility'] = 15
        else:
            breakdown['atr_volatility'] = 0
        
        # 3. Multi-timeframe confirmation (+20 points if aligned)
        if mtf_aligned:
            score += 20
            breakdown['mtf_confirmation'] = 20
        else:
            breakdown['mtf_confirmation'] = 0
        
        # 4. Trend strength bonus (+10 points for strong trends)
        ema5 = indicators.get('ema5', 0)
        ema20 = indicators.get('ema20', 0)
        
        if ema5 > 0 and ema20 > 0:
            trend_strength = abs(ema5 - ema20) / ema20
            if trend_strength > 0.001:  # Strong trend
                score += 10
                breakdown['trend_strength'] = 10
            else:
                breakdown['trend_strength'] = 0
        
        # 5. Price momentum (+5 points for strong momentum)
        close = indicators.get('close', 0)
        prev_close = indicators.get('prev_close', close)
        
        if prev_close > 0:
            momentum = (close - prev_close) / prev_close
            if abs(momentum) > 0.0005:  # Strong momentum
                score += 5
                breakdown['momentum'] = 5
            else:
                breakdown['momentum'] = 0
        
        # 6. Volume confirmation (+5 points if available)
        volume = indicators.get('volume', 0)
        avg_volume = indicators.get('avg_volume', 0)
        
        if avg_volume > 0 and volume > avg_volume * 1.2:
            score += 5
            breakdown['volume'] = 5
        else:
            breakdown['volume'] = 0
        
        # 7. Market session bonus (+5 points during active sessions)
        from strategy import is_trading_session
        if is_trading_session():
            score += 5
            breakdown['session'] = 5
        else:
            breakdown['session'] = 0
        
        # Ensure score doesn't exceed 100
        score = min(100, score)
        
        breakdown['total_score'] = score
        breakdown['minimum_required'] = self.minimum_score
        breakdown['signal_quality'] = self._get_signal_quality(score)
        
        return score, breakdown
    
    def _get_signal_quality(self, score):
        """
        Get signal quality description based on score
        """
        if score >= 80:
            return "EXCELLENT"
        elif score >= 70:
            return "GOOD"
        elif score >= 60:
            return "ACCEPTABLE"
        elif score >= 40:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def should_execute_trade(self, indicators, mtf_aligned=False):
        """
        Determine if trade should be executed based on signal score
        """
        score, breakdown = self.calculate_signal_score(indicators, mtf_aligned)
        
        should_execute = score >= self.minimum_score
        
        return should_execute, score, breakdown
    
    def get_signal_analysis(self, indicators, mtf_aligned=False):
        """
        Get comprehensive signal analysis
        """
        score, breakdown = self.calculate_signal_score(indicators, mtf_aligned)
        
        analysis = {
            'score': score,
            'breakdown': breakdown,
            'should_execute': score >= self.minimum_score,
            'quality': breakdown['signal_quality'],
            'recommendation': self._get_recommendation(score, breakdown)
        }
        
        return analysis
    
    def _get_recommendation(self, score, breakdown):
        """
        Get trading recommendation based on signal analysis
        """
        if score >= 80:
            return "STRONG_BUY" if breakdown.get('mtf_confirmation', 0) > 0 else "BUY"
        elif score >= 70:
            return "BUY"
        elif score >= 60:
            return "WEAK_BUY"
        elif score >= 40:
            return "WAIT"
        else:
            return "AVOID"
    
    def update_indicators_with_ma(self, data):
        """
        Update indicators with moving averages for better scoring
        """
        if data is None or len(data) < 20:
            return data
        
        # Calculate ATR moving average
        data['atr_ma'] = data['atr'].rolling(window=20).mean()
        
        # Calculate volume moving average if available
        if 'tick_volume' in data.columns:
            data['avg_volume'] = data['tick_volume'].rolling(window=20).mean()
        
        # Add previous close for momentum calculation
        data['prev_close'] = data['close'].shift(1)
        
        return data

# Global instance
signal_evaluator = SignalEvaluator() 