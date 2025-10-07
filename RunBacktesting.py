import ALPACA_Functions

## This is are test example, you can change the parameters to test different scenarios or use a different strategy from the ALPACA_Functions file
lead = "TSM"
lag = "NVDA"
lead_pct_increase = 1
lead_window_minutes = 10
lag_hold_minutes = 10
start_date = [2018, 1, 1]
end_date = [2024, 1, 1]

strategy = ALPACA_Functions.backtest_lead_lag_strategy(lead, lag, lead_pct_increase, lead_window_minutes, lag_hold_minutes, start_date, end_date)

hold = ALPACA_Functions.holding_returns(lag, start_date, end_date)

print(f"Returns for strategy: {strategy} vs holding: {hold}")