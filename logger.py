import csv
import datetime
import logging
from config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(CONFIG['log_file']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_trade(order_result):
    """
    Log trade execution result to CSV file
    """
    try:
        with open(CONFIG['trade_log_file'], mode="a", newline="") as file:
            writer = csv.writer(file)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Extract trade details
            if order_result:
                retcode = order_result.retcode
                comment = order_result.comment
                order_id = order_result.order if hasattr(order_result, 'order') else 'N/A'
                volume = order_result.volume if hasattr(order_result, 'volume') else 'N/A'
                price = order_result.price if hasattr(order_result, 'price') else 'N/A'
            else:
                retcode = 'FAILED'
                comment = 'Order result is None'
                order_id = 'N/A'
                volume = 'N/A'
                price = 'N/A'
            
            writer.writerow([now, retcode, comment, order_id, volume, price])
        
        logger.info(f"Logged trade at {now} with result code {retcode}")
        
    except Exception as e:
        logger.error(f"Error logging trade: {e}")

def log_signal(signal, indicators):
    """
    Log trading signal and indicators
    """
    try:
        with open("signal_log.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            writer.writerow([
                now, 
                signal, 
                indicators.get('ema5', 'N/A'),
                indicators.get('ema21', 'N/A'),
                indicators.get('rsi', 'N/A'),
                indicators.get('atr', 'N/A')
            ])
        
        logger.info(f"Signal generated: {signal} at {now}")
        
    except Exception as e:
        logger.error(f"Error logging signal: {e}")

def log_error(error_message, error_type="ERROR"):
    """
    Log error messages
    """
    logger.error(f"{error_type}: {error_message}")

def log_info(info_message):
    """
    Log info messages
    """
    logger.info(info_message)

def log_warning(warning_message):
    """
    Log warning messages
    """
    logger.warning(warning_message)

def create_trade_log_header():
    """
    Create header for trade log CSV file
    """
    try:
        with open(CONFIG['trade_log_file'], mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                'Timestamp', 
                'Result Code', 
                'Comment', 
                'Order ID', 
                'Volume', 
                'Price'
            ])
        logger.info("Created trade log header")
    except Exception as e:
        logger.error(f"Error creating trade log header: {e}")

def create_signal_log_header():
    """
    Create header for signal log CSV file
    """
    try:
        with open("signal_log.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                'Timestamp', 
                'Signal', 
                'EMA5', 
                'EMA21', 
                'RSI', 
                'ATR'
            ])
        logger.info("Created signal log header")
    except Exception as e:
        logger.error(f"Error creating signal log header: {e}")

# Initialize log files
def initialize_logs():
    """
    Initialize log files with headers
    """
    create_trade_log_header()
    create_signal_log_header() 