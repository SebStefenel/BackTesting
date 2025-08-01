from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime



with open("selected_stock.txt", "r") as f:
    stock = f.read().strip()

# Replace with your keys
ALPACA_API_KEY = "API_KEY"
ALPACA_SECRET_KEY = "Secret"

# Create Alpaca data client
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# Request 2-minute bars for AAPL
request_params = StockBarsRequest(
    symbol_or_symbols=[stock],
    timeframe=TimeFrame.Minute,
    start=datetime.datetime(2020, 7, 1),
    end=datetime.datetime(2024, 7, 2)
)

bars = client.get_stock_bars(request_params)

bars.df.to_csv(f"Info_{stock}.csv")