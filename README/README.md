# 📊 BackTesting Engine for Trading Strategies

## Overview

This project is a **BackTesting framework** designed to simulate and evaluate trading strategies using historical market data. It allows traders and developers to analyze the performance of algorithmic strategies **before risking real capital** in live markets.

This engine **leverages Alpaca Markets API** to retrieve accurate and up-to-date historical financial data, making it suitable for testing equity and crypto strategies with real market conditions.


## ✨ Current Features

- 🧠 **Lead-lag trading strategy**: Evaluate strategies where one stock is traded based on signals derived from another's performance (lead-lag behavior).
- ⏪ **Historical Data Replay (via Alpaca)**: Pull and test strategies over historical market data using the **Alpaca API**.

## 🚀 Getting Started

1. Clone this repository
2. Set your Alpaca API keys (https://alpaca.markets/)
3. Run `RunBacktesting.py` to simulate a lead-lag strategy