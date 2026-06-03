import pandas as pd
import numpy as np
from typing import Optional
from models.candle_snapshot import CandleSnapshot

from state.market_state import MarketState
from utils.config_manager import ConfigManager
from utils.logger import Logger

class LiquidityEngine:
    """
    Liquidity Engine
    ----------------
    Detects liquidity sweeps and imbalances.
    Now normalized by ATR for consistent signal strength across assets/volatility.
    """

    def __init__(self, market_state: MarketState, symbol: str, timeframe: str = "1m"):
        self.market_state = market_state
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = ConfigManager()
        self.logger = Logger(LiquidityEngine)

    # =====================================================
    # PUBLIC API
    # =====================================================

    def sweep_low(self, atr: float) -> float:
        """
        Bullish liquidity grab.
        Normalized by ATR: strength = (min_low - current_low) / ATR
        """
        snapshot = self.market_state.get_candle_snapshot(self.symbol, self.timeframe)
        if not snapshot: return 0.0

        df = self.market_state.get_candles_df(self.symbol, self.timeframe)
        if df.empty: return 0.0

        lookback = self.config.get("liquidity", "lookback_period") or 30
        if len(df) < lookback + 2: return 0.0

        window = df["low"].iloc[-lookback-1:-1]
        min_low = float(window.min())
        current_low = snapshot.low
        current_close = snapshot.close

        if current_low <= min_low:
            # ATR normalization
            strength = (min_low - current_low) / (atr + 1e-9)
            reclaim = 1.0 if current_close > min_low else 0.0
            return float(np.clip(strength + reclaim, 0.0, 1.0))

        return 0.0

    def sweep_high(self, atr: float) -> float:
        """
        Bearish liquidity grab.
        Normalized by ATR: strength = (current_high - max_high) / ATR
        """
        snapshot = self.market_state.get_candle_snapshot(self.symbol, self.timeframe)
        if not snapshot: return 0.0

        df = self.market_state.get_candles_df(self.symbol, self.timeframe)
        if df.empty: return 0.0

        lookback = self.config.get("liquidity", "lookback_period") or 30
        if len(df) < lookback + 2: return 0.0

        window = df["high"].iloc[-lookback-1:-1]
        max_high = float(window.max())
        current_high = snapshot.high
        current_close = snapshot.close

        if current_high >= max_high:
            # ATR normalization
            strength = (current_high - max_high) / (atr + 1e-9)
            reject = 1.0 if current_close < max_high else 0.0
            return float(np.clip(strength + reject, 0.0, 1.0))

        return 0.0
