from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime


# This gets the API key from a file on my computer, if you wish to use this code, please replace the file path with your own API key
def get_key():
    with open("C:\\Users\\sstefenel\\Desktop\\Alpaca.txt", "r", encoding="utf-8") as file:
        lines = file.read().splitlines()

    API_KEY = lines[0].split()[0]
    Secret = lines[0].split()[1]
    return [API_KEY, Secret]

# This functions recieves a stock symbol, as well as a start and end date writen in [year, month, day] pulls the data for a given stock symbola and returns the data as (i haven't decided yet) 
def pull_data(stock, start_date, end_date):
    key = get_key()
    ALPACA_API_KEY = key[0]
    ALPACA_SECRET_KEY = key[1]

    # Create Alpaca data client
    client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

    # Request 2-minute bars for AAPL
    request_params = StockBarsRequest(
        symbol_or_symbols=[stock],
        timeframe=TimeFrame.Minute,
        start=datetime.datetime(start_date[0], start_date[1], start_date[2]),
        end=datetime.datetime(end_date[0], end_date[1], end_date[2])
    )

    bars = client.get_stock_bars(request_params)

    return bars.df