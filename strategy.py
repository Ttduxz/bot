from datetime import datetime, time
from config import CONFIG
from indicators import get_volatility_filter
from modules.mtf_filter import mtf_filter
from modules.signal_evaluator import signal_evaluator
from modules.volatility_filter import volatility_filter
from modules.pause_manager import pause_manager

def is_trading_session():
    """
    Check if current time is within London or New York trading sessions
    """
    current_time = datetime.now().time()
    
    # London session (08:00-16:00 UTC)
    london_start = time(8, 0)
    london_end = time(16, 0)
    
    # New York session (13:00-21:00 UTC)
    ny_start = time(13, 0)
    ny_end = time(21, 0)
    
    # Check if current time is within either session
    in_london = london_start <= current_time <= london_end
    in_ny = ny_start <= current_time <= ny_end
    
    return in_london or in_ny

def check_momentum_filter(indicators):
    """
    Check if market has sufficient momentum for trading
    """
    # Check if price is moving in a clear direction
    ema_trend = abs(indicators['ema5'] - indicators['ema20']) / indicators['ema20']
    return ema_trend > 0.0001  # Minimum trend strength

def generate_signal(indicators, data=None):
    """
    Generate trading signal based on enhanced strategy (v3)
    Returns: "BUY", "SELL", or "NONE"
    """
    # 1. Check if we're in a trading session
    if not is_trading_session():
        return "NONE"
    
    # 2. Check pause manager conditions
    can_trade, pause_reason = pause_manager.can_trade()
    if not can_trade:
        return "NONE"
    
    # 3. Check volatility and momentum conditions
    if data is not None:
        skip_trading, vol_status = volatility_filter.should_skip_trading(data)
        if skip_trading:
            return "NONE"
    
    # 4. Check basic volatility filter
    if not get_volatility_filter(indicators['atr']):
        return "NONE"
    
    # 5. Check momentum filter
    if not check_momentum_filter(indicators):
        return "NONE"
    
    # 6. Get multi-timeframe confirmation
    mtf_signal = mtf_filter.get_mtf_signal()
    
    # 7. Generate base signal from M1 indicators
    base_signal = generate_base_signal(indicators)
    
    # 8. Combine signals and evaluate quality
    final_signal = combine_signals(base_signal, mtf_signal)
    
    # 9. Evaluate signal quality
    if final_signal != "NONE":
        should_execute, score, breakdown = signal_evaluator.should_execute_trade(
            indicators, 
            mtf_aligned=(mtf_signal == final_signal)
        )
        
        if not should_execute:
            return "NONE"
    
    return final_signal

def generate_base_signal(indicators):
    """
    Generate base signal from M1 indicators
    """
    # Trading logic: buy if ema5 > ema20 and RSI < 70
    # sell if ema5 < ema20 and RSI > 30
    if (indicators['ema5'] > indicators['ema20'] and 
        indicators['rsi'] < CONFIG['rsi_overbought']):
        return "BUY"
    elif (indicators['ema5'] < indicators['ema20'] and 
          indicators['rsi'] > CONFIG['rsi_oversold']):
        return "SELL"
    else:
        return "NONE"

def combine_signals(base_signal, mtf_signal):
    """
    Combine base signal with multi-timeframe signal
    """
    # If both signals agree, use that signal
    if base_signal == mtf_signal and base_signal != "NONE":
        return base_signal
    
    # If MTF signal is NONE, use base signal
    if mtf_signal == "NONE":
        return base_signal
    
    # If base signal is NONE, use MTF signal
    if base_signal == "NONE":
        return mtf_signal
    
    # If signals conflict, prefer MTF signal (higher timeframe)
    return mtf_signal

def calculate_dynamic_tp_sl(indicators, signal, current_price):
    """
    Calculate dynamic Take Profit and Stop Loss based on ATR (Updated v3)
    Stop Loss = ATR × 1.2
    Take Profit = ATR × 1.8
    """
    atr_value = indicators['atr']
    
    if signal == "BUY":
        # For buy orders: TP above, SL below
        take_profit = current_price + (atr_value * 1.8)  # ATR × 1.8 for TP
        stop_loss = current_price - (atr_value * 1.2)    # ATR × 1.2 for SL
    else:  # SELL
        # For sell orders: TP below, SL above
        take_profit = current_price - (atr_value * 1.8)  # ATR × 1.8 for TP
        stop_loss = current_price + (atr_value * 1.2)    # ATR × 1.2 for SL
    
    return take_profit, stop_loss

def get_comprehensive_signal_analysis(indicators, data=None):
    """
    Get comprehensive signal analysis including all filters
    """
    # Get multi-timeframe data
    mtf_success, mtf_message = mtf_filter.get_multi_timeframe_data(CONFIG['symbol'])
    
    # Generate signal
    signal = generate_signal(indicators, data)
    
    # Get MTF confirmation
    mtf_aligned = False
    if mtf_success:
        mtf_signal = mtf_filter.get_mtf_signal()
        mtf_aligned = (mtf_signal == signal)
    
    # Get signal evaluation
    analysis = signal_evaluator.get_signal_analysis(indicators, mtf_aligned)
    
    # Get volatility status
    vol_status = None
    if data is not None:
        vol_status = volatility_filter.get_volatility_status(data)
    
    # Get pause status
    pause_status = pause_manager.get_status()
    
    # Compile comprehensive analysis
    comprehensive_analysis = {
        'signal': signal,
        'mtf_success': mtf_success,
        'mtf_message': mtf_message,
        'mtf_aligned': mtf_aligned,
        'signal_analysis': analysis,
        'volatility_status': vol_status,
        'pause_status': pause_status,
        'trading_session': is_trading_session(),
        'timestamp': datetime.now()
    }
    
    return comprehensive_analysis

def update_indicators_for_v3(data):
    """
    Update indicators with additional calculations needed for v3
    """
    if data is None or len(data) < 50:
        return data
    
    # Update with moving averages for signal evaluation
    data = signal_evaluator.update_indicators_with_ma(data)
    
    # Add MACD histogram for momentum analysis
    histogram = volatility_filter.calculate_macd_histogram(data['close'])
    if histogram is not None:
        data['macd_histogram'] = histogram
    
    return data 