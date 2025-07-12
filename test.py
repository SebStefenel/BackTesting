import requests
from datetime import datetime
import time
from key import API_KEY

def to_unix_timestamp(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Convert a date string to a Unix timestamp (in seconds).
    
    Args:
        date_str (str): The date/time string (e.g., "2023-06-01 09:30:00")
        fmt (str): The format of the input string. Default: "%Y-%m-%d %H:%M:%S"
        
    Returns:
        int: Unix timestamp in seconds
    """
    dt = datetime.strptime(date_str, fmt)
    return int(time.mktime(dt.timetuple()))


url = 'https://finnhub.io/api/v1/stock/candle'
params = {
    'symbol': 'AAPL', 
    'resolution': '5',
    'from': to_unix_timestamp('2025-07-01 09:30:00'),
    'to': to_unix_timestamp('2025-07-01 16:00:00'),
    'token': API_KEY
}
response = requests.get(url, params=params)
data = response.json()
print(data)
