# 📊 BackTesting Engine for Trading Strategies

## 🧩 Overview
This project is a **modular backtesting framework** designed to **simulate and evaluate trading strategies** using **historical market data** from the [Alpaca Markets API](https://alpaca.markets/). It allows traders, analysts, and developers to test algorithmic trading ideas in a **controlled, data-driven environment** before deploying them in live markets. This engine is flexible enough to handle both **single-asset** and **multi-asset (lead-lag)** strategies and is easily extendable for custom trading logic.

---

## 📋 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Setup](#-setup)
- [Strategy Comparison](#-strategy-comparison-table)
- [Implemented Strategies](#-implemented-strategies)
- [Usage Examples](#-usage-examples)
- [Function Reference](#-function-reference)

---

## ✨ Features

### 🔁 Core Components
- ⚙️ **Historical Data Retrieval:** Fetches clean, minute-level historical data directly from the Alpaca API
- 🧮 **Backtesting Engine:** Runs defined strategy logic over historical price data and records simulated trades
- 📈 **Performance Metrics:** Automatically calculates total return, average trade return, and number of trades
- 🔄 **Multiple Strategy Support:** Includes 5 pre-built strategies (Lead-Lag, MA Crossover, RSI, Breakout, Bollinger Bands)
- 📊 **Buy-and-Hold Comparison:** Calculate holding returns to benchmark strategy performance

---

## 🛠 Installation

### Prerequisites
- Python 3.8+
- Alpaca Markets API account (free tier available)

### Required Libraries
```bash
pip install alpaca-py pandas numpy
```

---

## 🔐 Setup

### 1. Get Your Alpaca API Keys
1. Sign up at [Alpaca Markets](https://alpaca.markets/)
2. Navigate to your dashboard and generate API keys
3. Copy both your **API Key** and **Secret Key**

### 2. Configure API Access

Create a file named `API_Key.txt` in the project root directory with your credentials:

```
YOUR_API_KEY YOUR_SECRET_KEY
```

**Format:** Both keys on the **same line**, separated by a **space**.

### 3. Security Best Practices

⚠️ **IMPORTANT:** Never commit your API keys to version control!

The `.gitignore` file should already include:
```
API_Key.txt
```

If you're setting up this project for the first time:
1. Copy `API_Key.txt.example` to `API_Key.txt`
2. Replace the placeholder values with your actual keys
3. Verify `API_Key.txt` is listed in `.gitignore`

---

## ⚖️ Strategy Comparison Table

| Strategy | Type | Signal Basis | Ideal Market Condition | Example Use |
|-----------|------|---------------|------------------------|--------------| 
| **Lead-Lag** | Multi-Asset | % Move in leading stock | Correlated asset pairs | Cross-stock prediction |
| **Moving Average Crossover** | Trend Following | Short vs. Long SMA | Trending markets | "Golden/Death cross" setups |
| **RSI Mean Reversion** | Contrarian | RSI (momentum oscillator) | Range-bound markets | Buy oversold, sell overbought |
| **Breakout** | Momentum | Price > rolling high | Strong directional moves | Buy strength continuation |
| **Bollinger Bands Mean Reversion** | Volatility | Price vs. upper/lower bands | Sideways or reverting markets | Buy dips, sell rallies |

---

## 💡 Implemented Strategies

### 1. 🧠 Lead-Lag Strategy
Trade one stock (the *lagging stock*) based on significant percentage moves in another (the *leading stock*).

**Logic:**
- Detect when the *lead* stock increases by a given percentage within a set time window
- Buy the *lag* stock immediately and hold for a fixed period
- Record resulting profit or loss

**Parameters:**
- `lead_stock`: Symbol of the leading stock (e.g., "SPY")
- `lag_stock`: Symbol of the lagging stock (e.g., "QQQ")
- `lead_pct_increase`: Minimum percentage increase to trigger signal (e.g., 0.5 for 0.5%)
- `lead_window_minutes`: Time window to measure the percentage increase
- `lag_hold_minutes`: How long to hold the lagging stock position
- `start_date`: Start date as `[year, month, day]`
- `end_date`: End date as `[year, month, day]`

**Example:**
```python
backtest_lead_lag_strategy(
    lead_stock="SPY",
    lag_stock="QQQ",
    lead_pct_increase=0.5,
    lead_window_minutes=10,
    lag_hold_minutes=30,
    start_date=[2025, 9, 29],
    end_date=[2025, 10, 3]
)
```

---

### 2. 📈 Moving Average Crossover
Classic trend-following strategy using two simple moving averages.

**Logic:**
- **Buy Signal:** Short-term SMA crosses above long-term SMA (bullish crossover)
- **Sell Signal:** Short-term SMA crosses below long-term SMA (bearish crossover)
- Entries and exits occur at the next bar's close after the signal

**Parameters:**
- `stock`: Stock symbol (e.g., "AAPL")
- `short_window`: Period for short-term moving average (e.g., 10)
- `long_window`: Period for long-term moving average (e.g., 50)
- `start_date`: Start date as `[year, month, day]`
- `end_date`: End date as `[year, month, day]`

**Example:**
```python
backtest_ma_crossover(
    stock="AAPL",
    short_window=10,
    long_window=50,
    start_date=[2025, 1, 1],
    end_date=[2025, 3, 1]
)
```

---

### 3. 🔄 RSI Mean Reversion
Contrarian strategy that buys oversold conditions and sells overbought conditions.

**Logic:**
- **Buy Signal:** RSI drops below the oversold threshold (default: 30)
- **Sell Signal:** RSI rises above the overbought threshold (default: 70) OR hold period expires
- Uses a simple rolling average calculation for RSI

**Parameters:**
- `stock`: Stock symbol
- `period`: RSI calculation period (default: 14)
- `oversold`: RSI threshold for oversold condition (default: 30)
- `overbought`: RSI threshold for overbought condition (default: 70)
- `hold_minutes`: Maximum time to hold position (default: 60)
- `start_date`: Start date as `[year, month, day]`
- `end_date`: End date as `[year, month, day]`

**Example:**
```python
backtest_rsi_mean_reversion(
    stock="TSLA",
    period=14,
    oversold=30,
    overbought=70,
    hold_minutes=60,
    start_date=[2025, 2, 1],
    end_date=[2025, 2, 15]
)
```

---

### 4. 🚀 Breakout Strategy
Momentum strategy that enters when price breaks above recent highs.

**Logic:**
- **Buy Signal:** Current price breaks above the rolling high of the previous `lookback` bars
- **Exit:** After holding for `hold_minutes`
- Prevents overlapping trades by enforcing fixed hold times

**Parameters:**
- `stock`: Stock symbol
- `lookback`: Number of bars to calculate rolling high (e.g., 20)
- `hold_minutes`: How long to hold the position (default: 60)
- `start_date`: Start date as `[year, month, day]`
- `end_date`: End date as `[year, month, day]`

**Example:**
```python
backtest_breakout(
    stock="NVDA",
    lookback=20,
    hold_minutes=60,
    start_date=[2025, 3, 1],
    end_date=[2025, 3, 15]
)
```

---

### 5. 📊 Bollinger Bands Mean Reversion
Volatility-based mean reversion strategy using Bollinger Bands.

**Logic:**
- **Buy Signal:** Price crosses below the lower Bollinger Band
- **Exit:** Price crosses back above the middle band (SMA) OR hold period expires
- Uses standard deviation to define band width

**Parameters:**
- `stock`: Stock symbol
- `period`: Period for calculating SMA and standard deviation (default: 20)
- `num_std`: Number of standard deviations for bands (default: 2)
- `hold_minutes`: Maximum hold time (default: 60)
- `start_date`: Start date as `[year, month, day]`
- `end_date`: End date as `[year, month, day]`

**Example:**
```python
backtest_bollinger_mean_reversion(
    stock="AMZN",
    period=20,
    num_std=2,
    hold_minutes=60,
    start_date=[2025, 4, 1],
    end_date=[2025, 4, 15]
)
```

---

## 📝 Usage Examples

### Basic Workflow

```python
from ALPACA_Functions import *

# 1. Test a simple buy-and-hold strategy
holding_returns(
    stock="AAPL",
    start_date=[2025, 1, 1],
    end_date=[2025, 3, 1]
)

# 2. Run a moving average crossover backtest
ma_results = backtest_ma_crossover(
    stock="AAPL",
    short_window=10,
    long_window=50,
    start_date=[2025, 1, 1],
    end_date=[2025, 3, 1]
)

# 3. Compare with RSI strategy
rsi_results = backtest_rsi_mean_reversion(
    stock="AAPL",
    period=14,
    oversold=30,
    overbought=70,
    hold_minutes=60,
    start_date=[2025, 1, 1],
    end_date=[2025, 3, 1]
)

# 4. Analyze the results
print(ma_results)
print(rsi_results)
```

---

## 📚 Function Reference

### Core Functions

#### `pull_data(stock, start_date, end_date)`
Retrieves minute-level historical stock data from Alpaca.

**Returns:** Pandas DataFrame with columns: `open`, `high`, `low`, `close`, `volume`, `trade_count`, `vwap`

---

#### `holding_returns(stock, start_date, end_date)`
Calculates the simple buy-and-hold return for a stock over the specified period.

**Returns:** Float representing the percentage return

---

### Strategy Functions

All strategy functions return a Pandas DataFrame containing trade details:
- `entry_time`: Timestamp when position was opened
- `entry_price`: Price at entry
- `exit_time`: Timestamp when position was closed
- `exit_price`: Price at exit
- `return_pct`: Percentage return for the trade

Functions also print summary statistics including:
- Total number of trades
- Total return percentage
- Average return per trade

---

## 🔧 Customization

### Adding Your Own Strategy

To add a custom strategy, follow this pattern:

```python
def backtest_my_strategy(stock, param1, param2, start_date, end_date):
    # 1. Get data
    df = _prepare_df_for_backtest(pull_data(stock, start_date, end_date))
    
    if df.empty:
        print("No data.")
        return pd.DataFrame()
    
    # 2. Calculate indicators
    # ... your indicator logic here ...
    
    # 3. Generate signals and execute trades
    trades = []
    # ... your trading logic here ...
    
    # 4. Return results
    trades_df = pd.DataFrame(trades)
    
    if trades_df.empty:
        print("No trades generated.")
        return trades_df
    
    # 5. Print summary
    total = trades_df['return_pct'].sum()
    avg = trades_df['return_pct'].mean()
    print(f"My Strategy — trades: {len(trades_df)}, total %: {total:.4f}, avg %: {avg:.4f}")
    
    return trades_df
```

---

## ⚠️ Important Notes

### Data Limitations
- Alpaca provides minute-level data for backtesting
- Free tier accounts have rate limits on API calls
- Historical data availability may vary by stock and date range

### Strategy Considerations
- **Survivorship Bias:** Backtests use stocks that exist today; delisted stocks aren't included
- **Look-Ahead Bias:** Ensure signals use only historical data available at that point in time
- **Transaction Costs:** These backtests don't account for commissions, slippage, or spread
- **Market Impact:** Assumes you can always execute at the close price without affecting the market

### Performance Notes
- Past performance does not guarantee future results
- Always paper trade strategies before using real capital
- Consider risk management (stop losses, position sizing) before live trading

---

## 📄 License

This project is open source and available for educational and personal use.

---

## 🔗 Resources

- [Alpaca Markets API Documentation](https://alpaca.markets/docs/)
- [Alpaca-py Python Library](https://github.com/alpacahq/alpaca-py)
- [Technical Analysis Primer](https://www.investopedia.com/terms/t/technicalanalysis.asp)

---
