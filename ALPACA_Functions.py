from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime
import pandas as pd
import numpy as np

# This gets the API key from a file on my computer, if you wish to use this code, please replace the file path with your own API key
def get_key():
    with open('API_Key.txt', "r", encoding="utf-8") as file:
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

# This function implements a lead-lag strategy based on the parameters provided
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

        # ✅ Skip if the end of the window is not on the same calendar day
        if start_row['timestamp'].date() != end_row['timestamp'].date():
            continue

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

    if result_df.empty:
        print("No spikes detected that met the criteria.")
        return result_df

    # Calculate total and average return
    total_return = result_df['lag_return_pct'].sum()
    average_return = result_df['lag_return_pct'].mean()
    num_trades = len(result_df)

    print(f"\nTotal lag return over {num_trades} trades: {total_return:.4f}%")
    print(f"Average return per trade: {average_return:.4f}%")

    return total_return

# calculates the returns of holding a stock over a given time frame
def holding_returns(stock, start_date, end_date):
    df = pull_data(stock, start_date, end_date)
    if df.empty:
        print(f"No data for stock {stock}")
        return None

    # Calculate returns
    start_price = df.iloc[0]['close']
    end_price = df.iloc[-1]['close']
    return_pct = (end_price - start_price) / start_price * 100

    print(f"Holding {stock} from {start_date} to {end_date} yields a return of {return_pct:.2f}%")
    return return_pct


# helper to normalize dataframe returned by pull_data
def _prepare_df_for_backtest(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.reset_index(drop=True)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        df = df.set_index('timestamp')
    else:
        # if alpaca returned index already as timestamp
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
    return df

# Moving Average Crossover 
def backtest_ma_crossover(stock, short_window, long_window, start_date, end_date):
    """
    Buy when short SMA crosses above long SMA. Exit when short SMA crosses below long SMA.
    Entries/exits use next-bar close.
    Returns DataFrame of trades and prints summary.
    """
    df = _prepare_df_for_backtest(pull_data(stock, start_date, end_date))
    if df.empty:
        print("No data.")
        return pd.DataFrame()

    close = df['close'].astype(float)
    df['sma_short'] = close.rolling(window=short_window, min_periods=1).mean()
    df['sma_long'] = close.rolling(window=long_window, min_periods=1).mean()

    df['signal'] = 0
    df['signal'][short_window:] = np.where(df['sma_short'][short_window:] > df['sma_long'][short_window:], 1, 0)
    df['signal_shift'] = df['signal'].shift(1).fillna(0)
    df['cross_up'] = ((df['signal'] == 1) & (df['signal_shift'] == 0))
    df['cross_down'] = ((df['signal'] == 0) & (df['signal_shift'] == 1))

    trades = []
    in_trade = False
    entry_time, entry_price = None, None

    idxs = df.index
    for i in range(len(df)-1):  # use next bar to enter/exit
        ts = idxs[i]
        if df.loc[ts, 'cross_up'] and not in_trade:
            # enter at next bar close
            next_ts = idxs[i+1]
            entry_time = next_ts
            entry_price = df.loc[next_ts, 'close']
            in_trade = True

        if in_trade and df.loc[ts, 'cross_down']:
            # exit at next bar close (use same logic)
            next_ts = idxs[i+1]
            exit_time = next_ts
            exit_price = df.loc[next_ts, 'close']
            ret = (exit_price - entry_price) / entry_price * 100
            trades.append({
                'entry_time': entry_time, 'entry_price': entry_price,
                'exit_time': exit_time, 'exit_price': exit_price,
                'return_pct': ret
            })
            in_trade = False
            entry_time, entry_price = None, None

    # If we ended in a trade, close at last bar
    if in_trade:
        last_ts = idxs[-1]
        exit_time = last_ts
        exit_price = df.loc[last_ts, 'close']
        ret = (exit_price - entry_price) / entry_price * 100
        trades.append({
            'entry_time': entry_time, 'entry_price': entry_price,
            'exit_time': exit_time, 'exit_price': exit_price,
            'return_pct': ret
        })

    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        print("No MA crossover trades.")
        return trades_df

    total = trades_df['return_pct'].sum()
    avg = trades_df['return_pct'].mean()
    print(f"MA Crossover — trades: {len(trades_df)}, total %: {total:.4f}, avg %: {avg:.4f}")
    return trades_df

# RSI Mean Reversion
def backtest_rsi_mean_reversion(stock, period, oversold=30, overbought=70, hold_minutes=60, start_date=[2020,1,1], end_date=[2020,1,2]):
    """
    Buy when RSI < oversold, exit when RSI > overbought OR after hold_minutes have passed (whichever first).
    Uses simple rolling averages to compute RSI.
    """
    df = _prepare_df_for_backtest(pull_data(stock, start_date, end_date))
    if df.empty:
        print("No data.")
        return pd.DataFrame()

    close = df['close'].astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    df['rsi'] = rsi.fillna(50)

    trades = []
    in_trade = False
    entry_price = None
    entry_time = None
    idxs = df.index

    for i in range(len(df)-1):
        ts = idxs[i]
        next_ts = idxs[i+1]
        if (df.loc[ts, 'rsi'] < oversold) and (not in_trade):
            # enter next bar
            entry_time = next_ts
            entry_price = df.loc[next_ts, 'close']
            in_trade = True
            entry_idx = i+1

        if in_trade:
            # either RSI > overbought at current bar -> exit at next bar
            # or hold_minutes passed
            # check RSI at current ts
            if df.loc[ts, 'rsi'] > overbought:
                exit_time = next_ts
                exit_price = df.loc[next_ts, 'close']
                ret = (exit_price - entry_price) / entry_price * 100
                trades.append({
                    'entry_time': entry_time, 'entry_price': entry_price,
                    'exit_time': exit_time, 'exit_price': exit_price,
                    'return_pct': ret
                })
                in_trade = False
                entry_price, entry_time = None, None
            else:
                # check hold time
                hold_end_time = entry_time + pd.Timedelta(minutes=hold_minutes)
                if next_ts >= hold_end_time:
                    exit_time = next_ts
                    exit_price = df.loc[next_ts, 'close']
                    ret = (exit_price - entry_price) / entry_price * 100
                    trades.append({
                        'entry_time': entry_time, 'entry_price': entry_price,
                        'exit_time': exit_time, 'exit_price': exit_price,
                        'return_pct': ret
                    })
                    in_trade = False
                    entry_price, entry_time = None, None

    # if still in trade at end, close at last bar
    if in_trade:
        last_ts = idxs[-1]
        exit_price = df.loc[last_ts, 'close']
        ret = (exit_price - entry_price) / entry_price * 100
        trades.append({
            'entry_time': entry_time, 'entry_price': entry_price,
            'exit_time': last_ts, 'exit_price': exit_price,
            'return_pct': ret
        })

    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        print("No RSI trades.")
        return trades_df

    print(f"RSI — trades: {len(trades_df)}, total %: {trades_df['return_pct'].sum():.4f}, avg %: {trades_df['return_pct'].mean():.4f}")
    return trades_df

# Breakout
def backtest_breakout(stock, lookback, hold_minutes=60, start_date=[2020,1,1], end_date=[2020,1,2]):
    """
    Enter when price breaks above the rolling high of the previous `lookback` bars.
    Exit after hold_minutes.
    """
    df = _prepare_df_for_backtest(pull_data(stock, start_date, end_date))
    if df.empty:
        print("No data.")
        return pd.DataFrame()

    close = df['close'].astype(float)
    rolling_high = close.rolling(window=lookback, min_periods=lookback).max()
    df['rolling_high'] = rolling_high

    trades = []
    idxs = df.index
    in_trade = False
    entry_price = None
    entry_time = None

    for i in range(lookback, len(df)-1):
        ts = idxs[i]
        next_ts = idxs[i+1]
        # breakout if current close > previous rolling_high (previous window ends at i-1)
        prev_high = df['rolling_high'].iloc[i-1]
        if np.isnan(prev_high):
            continue
        if (df['close'].iloc[i] > prev_high) and not in_trade:
            # enter next bar
            entry_time = next_ts
            entry_price = df.loc[next_ts, 'close']
            in_trade = True
            # compute exit time by hold_minutes
            exit_time_target = entry_time + pd.Timedelta(minutes=hold_minutes)
            # find first bar >= exit_time_target
            future = df[df.index >= exit_time_target]
            if future.empty:
                # close at last bar
                exit_time = idxs[-1]
                exit_price = df.loc[exit_time, 'close']
            else:
                exit_time = future.index[0]
                exit_price = future.loc[exit_time, 'close']

            ret = (exit_price - entry_price) / entry_price * 100
            trades.append({
                'entry_time': entry_time, 'entry_price': entry_price,
                'exit_time': exit_time, 'exit_price': exit_price,
                'return_pct': ret
            })
            in_trade = False  # we use fixed hold-time, so no overlapping trades allowed

    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        print("No Breakout trades.")
        return trades_df

    print(f"Breakout — trades: {len(trades_df)}, total %: {trades_df['return_pct'].sum():.4f}, avg %: {trades_df['return_pct'].mean():.4f}")
    return trades_df

# 4) Bollinger Bands mean reversion (simple)
def backtest_bollinger_mean_reversion(stock, period=20, num_std=2, hold_minutes=60, start_date=[2020,1,1], end_date=[2020,1,2]):
    """
    Buy when price crosses below lower BB. Exit when price crosses above middle band (SMA) or after hold_minutes.
    """
    df = _prepare_df_for_backtest(pull_data(stock, start_date, end_date))
    if df.empty:
        print("No data.")
        return pd.DataFrame()

    close = df['close'].astype(float)
    sma = close.rolling(window=period, min_periods=period).mean()
    std = close.rolling(window=period, min_periods=period).std()
    df['bb_mid'] = sma
    df['bb_upper'] = sma + num_std * std
    df['bb_lower'] = sma - num_std * std

    trades = []
    idxs = df.index
    in_trade = False
    entry_price = None
    entry_time = None

    for i in range(period, len(df)-1):
        ts = idxs[i]
        next_ts = idxs[i+1]
        # entry: current close < lower band and we are not in trade
        if (df['close'].iloc[i] < df['bb_lower'].iloc[i]) and (not in_trade):
            entry_time = next_ts
            entry_price = df.loc[next_ts, 'close']
            in_trade = True
            # now look forward for exit condition: close >= mid band OR hold_minutes elapsed
            # check subsequent bars
            for j in range(i+1, len(df)):
                t2 = idxs[j]
                price2 = df.loc[t2, 'close']
                mid2 = df.loc[t2, 'bb_mid']
                if not np.isnan(mid2) and price2 >= mid2:
                    exit_time = t2
                    exit_price = price2
                    ret = (exit_price - entry_price) / entry_price * 100
                    trades.append({
                        'entry_time': entry_time, 'entry_price': entry_price,
                        'exit_time': exit_time, 'exit_price': exit_price,
                        'return_pct': ret
                    })
                    in_trade = False
                    break
                # check hold timeout
                if t2 >= (entry_time + pd.Timedelta(minutes=hold_minutes)):
                    exit_time = t2
                    exit_price = price2
                    ret = (exit_price - entry_price) / entry_price * 100
                    trades.append({
                        'entry_time': entry_time, 'entry_price': entry_price,
                        'exit_time': exit_time, 'exit_price': exit_price,
                        'return_pct': ret
                    })
                    in_trade = False
                    break

    # close any remaining open trade at last bar
    if in_trade:
        last_ts = idxs[-1]
        exit_price = df.loc[last_ts, 'close']
        ret = (exit_price - entry_price) / entry_price * 100
        trades.append({
            'entry_time': entry_time, 'entry_price': entry_price,
            'exit_time': last_ts, 'exit_price': exit_price,
            'return_pct': ret
        })

    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        print("No Bollinger trades.")
        return trades_df

    print(f"Bollinger — trades: {len(trades_df)}, total %: {trades_df['return_pct'].sum():.4f}, avg %: {trades_df['return_pct'].mean():.4f}")
    return trades_df