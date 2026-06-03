import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from typing import Optional, Dict
from models.candle_snapshot import CandleSnapshot

from state.market_state import MarketState
from utils.config_manager import ConfigManager
from utils.logger import Logger

class StructureEngine:
    """
    Market Structure Engine
    -----------------------
    Identifies BOS (Break of Structure) and key levels.
    Optimized for cached data and volatility normalization.
    """

    def __init__(self, market_state: MarketState, symbol: str, timeframe: str = "1m"):
        self.market_state = market_state
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = ConfigManager()
        self.logger = Logger(StructureEngine)

        self._cache = {}
        self._last_candle_time = None

    # =====================================================
    # CORE COMPUTATION
    # =====================================================

    def _compute_structure(self, df: pd.DataFrame):
        """
        Identifies swing highs/lows and key levels in one pass.
        """
        if df.empty:
            self._cache = {}
            return

        swing_window = self.config.get("structure", "SWING_WINDOW") or 5

        highs = df["high"].to_numpy(dtype=np.float64)
        lows = df["low"].to_numpy(dtype=np.float64)

        swing_highs = argrelextrema(highs, np.greater, order=swing_window)[0]
        swing_lows = argrelextrema(lows, np.less, order=swing_window)[0]

        limit = len(df) - 1 - swing_window
        confirmed_highs = swing_highs[swing_highs <= limit]
        confirmed_lows = swing_lows[swing_lows <= limit]

        resistance = float(df["high"].iloc[confirmed_highs[-1]]) if len(confirmed_highs) > 0 else None
        support = float(df["low"].iloc[confirmed_lows[-1]]) if len(confirmed_lows) > 0 else None

        self._cache = {
            "resistance": resistance,
            "support": support,
            "timestamp": df.index[-1]
        }

    def _ensure_computed(self):
        snapshot = self.market_state.get_candle_snapshot(self.symbol, self.timeframe)
        if not snapshot:
            return

        df = self.market_state.get_candles_df(self.symbol, self.timeframe)
        if df.empty:
            return

        if self._last_candle_time != snapshot.timestamp or not self._cache:
            self._compute_structure(df)
            self._last_candle_time = snapshot.timestamp

    # =====================================================
    # PUBLIC API
    # =====================================================

    def bos_up(self, atr: float) -> float:
        self._ensure_computed()

        if not self._cache or self._cache["resistance"] is None or atr <= 0:
            return 0.0

        df = self.market_state.get_candles_df(self.symbol, self.timeframe)
        close = float(df["close"].iloc[-1])
        displacement = close - self._cache["resistance"]

        if displacement <= 0:
            return 0.0

        return float(np.clip(displacement / atr, 0.0, 1.0))

    def bos_down(self, atr: float) -> float:
        self._ensure_computed()

        if not self._cache or self._cache["support"] is None or atr <= 0:
            return 0.0

        df = self.market_state.get_candles_df(self.symbol, self.timeframe)
        close = float(df["close"].iloc[-1])
        displacement = self._cache["support"] - close

        if displacement <= 0:
            return 0.0

        return float(np.clip(displacement / atr, 0.0, 1.0))

    def get_key_levels(self) -> tuple[Optional[float], Optional[float]]:
        self._ensure_computed()
        return self._cache.get("resistance"), self._cache.get("support")
