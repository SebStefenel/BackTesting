# 📊 BackTesting Engine for Trading Strategies

## 🧩 Overview

This project is a **modular backtesting framework** designed to **simulate and evaluate trading strategies** using **historical market data** from the [Alpaca Markets API](https://alpaca.markets/).  

It allows traders, analysts, and developers to test algorithmic trading ideas in a **controlled, data-driven environment** before deploying them in live markets.

This engine is flexible enough to handle both **single-asset** and **multi-asset (lead-lag)** strategies and is easily extendable for custom trading logic.

---

## ⚖️ Strategy Comparison Table

| Strategy | Type | Signal Basis | Ideal Market Condition | Example Use |
|-----------|------|---------------|------------------------|--------------|
| **Lead-Lag** | Multi-Asset | % Move in leading stock | Correlated asset pairs | Cross-stock prediction |
| **Moving Average Crossover** | Trend Following | Short vs. Long SMA | Trending markets | “Golden/Death cross” setups |
| **RSI Mean Reversion** | Contrarian | RSI (momentum oscillator) | Range-bound markets | Buy oversold, sell overbought |
| **Breakout** | Momentum | Price > rolling high | Strong directional moves | Buy strength continuation |
| **Bollinger Bands Mean Reversion** | Volatility | Price vs. upper/lower bands | Sideways or reverting markets | Buy dips, sell rallies |

---


## ✨ Features

### 🔁 Core Components
- ⚙️ **Historical Data Retrieval:**  
  Fetches clean, minute-level (or other timeframe) historical data directly from the Alpaca API.

- 🧮 **Backtesting Engine:**  
  Runs defined strategy logic over historical price data and records simulated trades.

- 📈 **Performance Metrics:**  
  Automatically calculates total return, average trade return, and number of trades.

---

## 💡 Implemented Strategies

### 1. 🧠 Lead-Lag Strategy
Trade one stock (the *lagging stock*) based on significant percentage moves in another (the *leading stock*).  

**Logic:**
- Detect when the *lead* stock increases by a given percentage within a set time window.  
- Buy the *lag* stock immediately and hold for a fixed period.  
- Record resulting profit or loss.

**Example Use:**
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
