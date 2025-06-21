import MetaTrader5 as mt5
from config import CONFIG
from strategy import calculate_dynamic_tp_sl

def initialize_mt5():
    """
    Initialize MetaTrader 5 connection
    """
    if not mt5.initialize():
        print("MT5 initialize failed")
        return False
    
    # Login to MT5 account
    if CONFIG['mt5_login'] and CONFIG['mt5_password']:
        if not mt5.login(login=CONFIG['mt5_login'], 
                        password=CONFIG['mt5_password'], 
                        server=CONFIG['mt5_server']):
            print("MT5 login failed")
            return False
    
    print("MT5 connected successfully")
    return True

def get_current_price(symbol):
    """
    Get current bid/ask prices for the symbol
    """
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None, None
    
    return tick.bid, tick.ask

def place_order(symbol, signal, volume, indicators=None):
    """
    Place a market order with dynamic TP/SL
    """
    # Get current prices
    bid, ask = get_current_price(symbol)
    if bid is None or ask is None:
        return None
    
    # Determine order type and price
    if signal == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = ask
        sl_price = bid - (CONFIG['stop_loss_pips'] * 0.1)  # Convert pips to price
        tp_price = ask + (CONFIG['take_profit_pips'] * 0.1)
    else:  # SELL
        order_type = mt5.ORDER_TYPE_SELL
        price = bid
        sl_price = ask + (CONFIG['stop_loss_pips'] * 0.1)
        tp_price = bid - (CONFIG['take_profit_pips'] * 0.1)
    
    # Use dynamic TP/SL if indicators are provided
    if indicators is not None:
        tp_price, sl_price = calculate_dynamic_tp_sl(indicators, signal, price)
    
    # Prepare order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": CONFIG['deviation'],
        "magic": CONFIG['magic_number'],
        "comment": "XAUUSD Scalping Bot order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    
    # Send order
    result = mt5.order_send(request)
    return result

def close_position(ticket):
    """
    Close a specific position by ticket number
    """
    position = mt5.positions_get(ticket=ticket)
    if not position:
        return None
    
    position = position[0]
    
    # Determine close order type
    if position.type == mt5.POSITION_TYPE_BUY:
        close_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(position.symbol).bid
    else:
        close_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(position.symbol).ask
    
    # Prepare close request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": close_type,
        "position": ticket,
        "price": price,
        "deviation": CONFIG['deviation'],
        "magic": CONFIG['magic_number'],
        "comment": "XAUUSD Scalping Bot close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    
    result = mt5.order_send(request)
    return result

def get_open_positions():
    """
    Get all open positions for the bot
    """
    positions = mt5.positions_get()
    if positions is None:
        return []
    
    # Filter positions by magic number
    bot_positions = [pos for pos in positions if pos.magic == CONFIG['magic_number']]
    return bot_positions

def get_position_count():
    """
    Get number of open positions for the bot
    """
    positions = get_open_positions()
    return len(positions)

def check_max_positions():
    """
    Check if we can open more positions
    """
    current_positions = get_position_count()
    return current_positions < CONFIG['max_positions'] 