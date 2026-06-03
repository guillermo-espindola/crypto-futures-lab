# Institutional Quant Trading System (Binance Futures)

Modular high-frequency trading system focused on market microstructure and probabilistic signals.

## ⚙️ General Configuration
Managed in `config/settings.py`:
- **Symbol**: Trading pair (e.g., UBUSDT).
- **Risk**: Max risk per trade, total exposure, and drawdown kill-switch.
- **Execution**: Latency simulation and fee models.
- **Infrastructure**: Kafka bootstrap servers and topic names.

## 🚀 Features

| Feature | Description | Input | Output |
| :--- | :--- | :--- | :--- |
| **Kafka Ingestion** | Async real-time data streaming | JSON Kafka Topics | Validated Models |
| **Market State** | Bounded realtime state manager | Market Events | Time-series / Orderbooks |
| **Structure Engine** | Market structure (BOS/CHOCH) | Candles | Signal (0.0 or 1.0) |
| **Liquidity Engine** | Sweeps & Imbalances (FVG) | Candles | Signal (0.0 or 1.0) |
| **Flow Engine** | Delta & Order Flow Absorption | Trades | Signal (0.0 or 1.0) |
| **Regime Engine** | Volatility & Trend Analysis | Candles | Signal (0.0 or 1.0) |
| **Scoring Engine** | Probabilistic ensemble scoring | Engine Signals | Probability (0.0 to 1.0) |
| **Risk Engine** | Exposure & Drawdown control | Equity / Balance | Approved Size/Limit |
| **Execution Engine** | Latency-aware simulated orders | Orders | TradeExecution result |
| **Portfolio Engine** | PnL & Exposure tracking | Mark Prices | Portfolio Snapshot |

## 🛠️ Quick Start
```bash
python main.py
```
