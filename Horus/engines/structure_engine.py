import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from typing import Optional

from config.config_manager import ConfigManager
from state.market_state import MarketState
from utils.logger_interface import ILogger

class StructureEngine:
    """
    Market Structure Engine
    -----------------------
    Identifies BOS (Break of Structure) and key levels.
    Optimized for cached data and volatility normalization.
    """

    def __init__(self, market_state: MarketState, timeframe: str, config_manager: ConfigManager, logger: ILogger):
        self._market_state = market_state
        self._timeframe = timeframe
        self._config = config_manager
        self._logger = logger

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

        swing_window = self._config.get_config().structure.swing_window

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
        snapshot = self._market_state.get_candle_snapshot(self._timeframe)
        if not snapshot:
            return

        df = self._market_state.get_timeframe_candles_df(self._timeframe)
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

        df = self._market_state.get_timeframe_candles_df(self._timeframe)
        close = float(df["close"].iloc[-1])
        displacement = close - self._cache["resistance"]

        if displacement <= 0:
            return 0.0

        return float(np.clip(displacement / atr, 0.0, 1.0))

    def bos_down(self, atr: float) -> float:
        self._ensure_computed()

        if not self._cache or self._cache["support"] is None or atr <= 0:
            return 0.0

        df = self._market_state.get_timeframe_candles_df(self._timeframe)
        close = float(df["close"].iloc[-1])
        displacement = self._cache["support"] - close

        if displacement <= 0:
            return 0.0

        return float(np.clip(displacement / atr, 0.0, 1.0))

    def get_key_levels(self) -> tuple[Optional[float], Optional[float]]:
        self._ensure_computed()
        return self._cache.get("resistance"), self._cache.get("support")
