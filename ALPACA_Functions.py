from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime
import pandas as pd


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

def backtest_lead_lag_strategy(
    lead_stock: str,
    lag_stock: str,
    lead_pct_increase: float,
    lead_window_minutes: int,
    lag_hold_minutes: int,
    start_date: list,  # e.g., [2020, 7, 1]
    end_date: list     # e.g., [2020, 7, 3]
):
    # 1. Pull data for lead stock
    lead_df = pull_data(lead_stock, start_date, end_date)
    if lead_df.empty:
        print(f"No data for lead stock {lead_stock}")
        return

    # 2. Pull broader data for lagging stock
    lag_df = pull_data(lag_stock, start_date, end_date)
    if lag_df.empty:
        print(f"No data for lag stock {lag_stock}")
        return

    # 3. Ensure datetime index
    lead_df = lead_df.reset_index()
    lag_df = lag_df.reset_index()
    lead_df['timestamp'] = pd.to_datetime(lead_df['timestamp'])
    lag_df['timestamp'] = pd.to_datetime(lag_df['timestamp'])

    lead_df = lead_df.sort_values("timestamp")
    lag_df = lag_df.sort_values("timestamp")

    spike_signals = []

    for i in range(len(lead_df) - lead_window_minutes):
        start_row = lead_df.iloc[i]
        end_row = lead_df.iloc[i + lead_window_minutes]

        pct_change = (end_row['close'] - start_row['close']) / start_row['close'] * 100

        if pct_change >= lead_pct_increase:
            spike_time = end_row['timestamp']

            # Buy lagging stock at this timestamp
            lag_start = lag_df[lag_df['timestamp'] >= spike_time]
            if lag_start.empty:
                continue
            lag_entry_row = lag_start.iloc[0]
            lag_entry_price = lag_entry_row['close']
            lag_entry_time = lag_entry_row['timestamp']

            # Sell after holding period
            lag_exit_time = lag_entry_time + pd.Timedelta(minutes=lag_hold_minutes)
            lag_exit_df = lag_df[lag_df['timestamp'] >= lag_exit_time]
            if lag_exit_df.empty:
                continue
            lag_exit_price = lag_exit_df.iloc[0]['close']

            return_pct = (lag_exit_price - lag_entry_price) / lag_entry_price * 100

            spike_signals.append({
                "lead_spike_time": spike_time,
                "lead_pct_change": pct_change,
                "lag_entry_price": lag_entry_price,
                "lag_exit_price": lag_exit_price,
                "lag_return_pct": return_pct
            })

    result_df = pd.DataFrame(spike_signals)
    print(result_df)
    return result_df