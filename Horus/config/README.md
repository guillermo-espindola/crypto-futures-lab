```json
{
  "current_mode": "SOFT",
  "modes": {
    "SOFT": {
      "risk": {
        "max_risk_per_trade": 0.010,
        "max_leverage": 10,
        "max_drawdown": 0.20
      },
      "scoring": {
        "ema_alpha": 0.35,
        "confirmation_threshold": 1,
        "long_bias_weight": 0.65,
        "flow_weight": 0.25,
        "regime_weight": 0.10
      },
      "liquidity": {
        "lookback_period": 20,
        "sweep_sensitivity": 0.6
      },
      "order_flow": {
        "window_size": 30,
        "impact_sensitivity": 1.2
      },
      "execution": {
        "slippage_factor": 0.001,
        "latency_ms": 30,
        "taker_fee": 0.0005
      },
      "behavior": {
        "allow_more_trades": true,
        "cooldown_seconds": 3,
        "noise_tolerance": "high"
      }
    },
    "MODERATE": {
      "risk": {
        "max_risk_per_trade": 0.01,
        "max_leverage": 5,
        "max_drawdown": 0.15
      },
      "scoring": {
        "ema_alpha": 0.25,
        "confirmation_threshold": 2,
        "long_bias_weight": 0.60,
        "flow_weight": 0.30,
        "regime_weight": 0.10
      },
      "liquidity": {
        "lookback_period": 30,
        "sweep_sensitivity": 0.75
      },
      "order_flow": {
        "window_size": 50,
        "impact_sensitivity": 1.0
      },
      "execution": {
        "slippage_factor": 0.0005,
        "latency_ms": 50,
        "taker_fee": 0.0004
      },
      "behavior": {
        "allow_more_trades": "balanced",
        "cooldown_seconds": 10,
        "noise_tolerance": "medium"
      }
    },
    "STRICT": {
      "risk": {
        "max_risk_per_trade": 0.005,
        "max_leverage": 3,
        "max_drawdown": 0.10
      },
      "scoring": {
        "ema_alpha": 0.15,
        "confirmation_threshold": 3,
        "long_bias_weight": 0.50,
        "flow_weight": 0.35,
        "regime_weight": 0.15
      },
      "liquidity": {
        "lookback_period": 50,
        "sweep_sensitivity": 0.9
      },
      "order_flow": {
        "window_size": 100,
        "impact_sensitivity": 0.8
      },
      "execution": {
        "slippage_factor": 0.0003,
        "latency_ms": 80,
        "taker_fee": 0.0003
      },
      "behavior": {
        "allow_more_trades": false,
        "cooldown_seconds": 20,
        "noise_tolerance": "low"
      }
    }
  },
  "general": {
    "symbol": "UBUSDT",
    "time_frame": "1m",
    "time_frames": ["1m"],
    "max_candles": 250,
    "initial_balance": 10000.0
  }
}
```