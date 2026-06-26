import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from typing import Optional
from config.config_manager import ConfigManager
from state.market_state import MarketState
from utils.logger_interface import ILogger
class StructureEngine:
    def __init__(self, market_state: MarketState, timeframe: str, config_manager: ConfigManager, logger: ILogger):
        self._market_state = market_state
        self._timeframe = timeframe
        self._config = config_manager
        self._logger = logger
        self._cache = {}
        self._last_candle_time = None
    def _compute_structure(self, df: pd.DataFrame):
        if df.empty:
            self._cache = {}
            return
        swing_window = self._config.get_config().structure.swing_window
        highs = df["high"].to_numpy(dtype=np.float64)
        lows = df["low"].to_numpy(dtype=np.float64)
        swing_high_idx = argrelextrema(highs, np.greater, order=swing_window)[0]
        swing_low_idx = argrelextrema(lows, np.less, order=swing_window)[0]
        if len(swing_high_idx) == 0 or len(swing_low_idx) == 0:
            self._cache = {"resistance": None, "support": None, "timestamp": df.index[-1]}
            return
        current_price = float(df["close"].iloc[-1])
        bin_size = current_price * 0.001
        def find_strong_level(indices, values, is_high: bool):
            prices = values[indices]
            if len(prices) == 0: return None
            bins = np.arange(min(prices) - bin_size, max(prices) + bin_size, bin_size)
            hist, bin_edges = np.histogram(prices, bins=bins)
            max_bin = np.argmax(hist)
            strong_level = (bin_edges[max_bin] + bin_edges[max_bin+1]) / 2
            return float(strong_level)
        resistance = find_strong_level(swing_high_idx, highs, True)
        support = find_strong_level(swing_low_idx, lows, False)
        self._cache = {"resistance": resistance, "support": support, "timestamp": df.index[-1]}
    def _ensure_computed(self):
        snapshot = self._market_state.get_candle_snapshot(self._timeframe)
        if not snapshot: return
        df = self._market_state.get_timeframe_candles_df(self._timeframe)
        if df.empty: return
        if self._last_candle_time != snapshot.timestamp or not self._cache:
            self._compute_structure(df)
            self._last_candle_time = snapshot.timestamp
    def bos_up(self, atr: float) -> float:
        self._ensure_computed()
        if not self._cache or self._cache["resistance"] is None or atr <= 0: return 0.0
        df = self._market_state.get_timeframe_candles_df(self._timeframe)
        close = float(df["close"].iloc[-1])
        displacement = close - self._cache["resistance"]
        if displacement <= 0: return 0.0
        return float(np.clip(displacement / atr, 0.0, 1.0))
    def bos_down(self, atr: float) -> float:
        self._ensure_computed()
        if not self._cache or self._cache["support"] is None or atr <= 0: return 0.0
        df = self._market_state.get_timeframe_candles_df(self._timeframe)
        close = float(df["close"].iloc[-1])
        displacement = self._cache["support"] - close
        if displacement <= 0: return 0.0
        return float(np.clip(displacement / atr, 0.0, 1.0))
    def get_key_levels(self) -> tuple[Optional[float], Optional[float]]:
        self._ensure_computed()
        return self._cache.get("resistance"), self._cache.get("support")
