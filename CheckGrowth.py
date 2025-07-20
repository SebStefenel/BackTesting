import pandas as pd

expected_percent_change = 5
time_span = 1 # this is in reference to sets of 2 minutes

df = pd.read_csv("Info.csv", parse_dates=True, index_col="timestamp")

# Remove multi-index if it's there
if "symbol" in df.columns:
    df = df.drop(columns=["symbol"])

# Optional: reset index if timestamp is nested
df.index = pd.to_datetime(df.index)

# Track matches
matches = []

# Loop through rows to check 2-minute % change
for i in range(len(df) - 2):
    price_now = df.iloc[i]["close"]
    price_later = df.iloc[i + time_span]["close"]
    percent_change = ((price_later - price_now) / price_now) * 100

    if percent_change >= expected_percent_change:
        print(f"\n🚀 Found {percent_change}% increase at {df.index[i]}:")
        print(df.iloc[i:i+3])  # Print the 3 rows: current + next 2
        matches.append(df.iloc[i:i+3])

# Optional: save matches to file
if matches:
    result_df = pd.concat(matches)
    result_df.to_csv("price_spikes.csv")
    print(f"\n✅ Saved {len(matches)} matching windows to price_spikes.csv")
else:
    print(f"\n❌ No {expected_percent_change}% price increases over {time_span} minutes found.")
