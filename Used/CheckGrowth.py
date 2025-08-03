import pandas as pd

with open("stock.txt", "r") as f:
    contents = f.read().strip()
    stock, stockB = contents.split()


with open("perameters.txt", "r") as f:
    contents = f.read().strip()

# Split the string by spaces and convert to integers
expected_percent_change, time_span, stockB_time_span = map(int, contents.split())

# Load the stock data
df = pd.read_csv(f"Info_{stock}.csv", parse_dates=True, index_col="timestamp")

# Remove multi-index if it's there
if "symbol" in df.columns:
    df = df.drop(columns=["symbol"])

# Ensure datetime index
df.index = pd.to_datetime(df.index)

# Track matches
matches = []
match_time = []  # To store date/time and closing prices

# Loop through rows to check % change over time_span minutes
for i in range(len(df) - time_span):
    price_now = df.iloc[i]["close"]
    price_later = df.iloc[i + time_span]["close"]
    percent_change = ((price_later - price_now) / price_now) * 100

    if percent_change >= expected_percent_change:
        #print(f"\n🚀 Found {percent_change:.2f}% increase at {df.index[i]}:")
        #print(df.iloc[i:i+time_span+1])

        # Add full matching window
        matches.append(df.iloc[i:i+time_span+1])

        # Record date/time and closing prices
        match_time = df.index[i + time_span]
        match_price_now = price_now
        match_price_later = price_later
        match_time.append(match_time)

# Output results
if matches:
    result_df = pd.concat(matches)
    result_df.to_csv("price_spikes.csv")
    #print(f"\n✅ Saved {len(matches)} matching windows to price_spikes.csv")
else:
    print(f"\n❌ No {expected_percent_change}% price increases over {time_span} minutes found.")

def evaluate_stockB_response(match_times, stockB_symbol, stockB_time_span):
    # Load stockB data
    df_b = pd.read_csv(f"Info_{stockB_symbol}.csv", parse_dates=True, index_col="timestamp")

    # Clean up
    if "symbol" in df_b.columns:
        df_b = df_b.drop(columns=["symbol"])
    df_b.index = pd.to_datetime(df_b.index)

    # Store results
    responses = []

    for t in match_times:
        try:
            # Get the price of stockB at the same time as stockA's spike
            price_start = df_b.loc[t]["close"]

            # Find the timestamp stockB_time_span minutes later
            future_time = t + pd.Timedelta(minutes=stockB_time_span)

            # Get the closing price at that future time
            price_end = df_b.loc[future_time]["close"]

            # Calculate price change (you can also use percent if preferred)
            change = price_end - price_start
            percent_change = ((price_end - price_start) / price_start) * 100

            responses.append((t, price_start, price_end, change, percent_change))
        except KeyError:
            # Handle missing timestamps (e.g., market closed, gap, etc.)
            print(f"⚠️ Missing data for {t} or {future_time} in stockB")
            continue

    return responses
