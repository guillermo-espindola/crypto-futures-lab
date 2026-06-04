import numpy as np
import pandas as pd
from typing import Dict, Optional
from models.candle_snapshot import CandleSnapshot

from state.market_state import MarketState
from utils.config_manager import ConfigManager
from utils.logger_interface import ILogger

class RegimeEngine:
    """
    Advanced Market Regime Engine
    ---------------------------------
    Detects Trend strength, Volatility regime, and Market efficiency.
    Optimized to use CandleSnapshots and dynamic execution feedback.
    """

    def __init__(self, market_state: MarketState, symbol: str, timeframe: str, config_manager: ConfigManager, logger: ILogger):
        self.market_state = market_state
        self.symbol = symbol
        self.timeframe = timeframe
        self.config = config_manager
        self.logger = logger

        # Cache for the current candle's results
        self._current_results = {}
        self._last_candle_time = None

        # Feedback loop: Adjusts internal volatility expectation based on actual slippage
        self._volatility_adjustment = 1.0

    # =====================================================
    # CORE COMPUTATION
    # =====================================================

    def _compute_regime_metrics(self, df: pd.DataFrame, snapshot: CandleSnapshot):
        """
        Performs all regime calculations in a single pass.
        """
        if df.empty:
            self._current_results = {}
            return

        period = self.config.get("regime", "DEFAULT_PERIOD") or 14

        # 1. ATR is now provided by the snapshot
        current_atr = snapshot.atr

        # 2. Chop Index (Needs history, so we use DF)
        chop_score = self._calculate_chop(df, period)

        # 3. Efficiency Ratio (Needs history, so we use DF)
        er_series = self._calculate_efficiency_ratio(df, period=20)
        current_er = er_series.iloc[-1]

        # 4. Volatility Regime
        # We use the snapshot's ATR and our internal feedback adjustment
        baseline_atr = df['high'].diff().abs().ewm(span=period, adjust=False).mean().iloc[-1]
        vol_ratio = (current_atr * self._volatility_adjustment) / (baseline_atr + 1e-9)
        vol_score = (np.tanh((vol_ratio - 1.0) * 2.0) + 1.0) / 2.0

        # Store results
        self._current_results = {
            "atr": current_atr,
            "trend": float(np.clip(0.6 * (1.0 - chop_score/100.0) + 0.4 * current_er, 0.0, 1.0)),
            "volatility": float(np.clip(vol_score, 0.0, 1.0)),
            "efficiency": float(np.clip(current_er, 0.0, 1.0)),
            "timestamp": snapshot.timestamp
        }

    def _calculate_chop(self, df: pd.DataFrame, period: int) -> float:
        high_max = df["high"].rolling(period).max()
        low_min = df["low"].rolling(period).min()

        high, low, close = df["high"], df["low"], df["close"]
        tr = pd.concat([
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs()
        ], axis=1).max(axis=1)
        atr_sum = tr.rolling(period).sum()

        range_val = (high_max - low_min).replace(0, np.nan)
        chop = 100 * np.log10(atr_sum / range_val) / np.log10(period)
        return float(chop.iloc[-1]) if not chop.empty else 50.0

    def _calculate_efficiency_ratio(self, df: pd.DataFrame, period: int) -> pd.Series:
        close = df["close"]
        direction = (close - close.shift(period)).abs()
        volatility = close.diff().abs().rolling(period).sum()
        return (direction / volatility.replace(0, np.nan)).fillna(0)

    # =====================================================
    # PUBLIC API
    # =====================================================

    def apply_execution_feedback(self, relative_slippage: float):
        """
        Adjusts the volatility baseline based on real market friction.
        """
        expected_slippage = self.config.get("execution", "slippage_factor") or 0.0005
        ratio = relative_slippage / (expected_slippage + 1e-9)

        alpha = 0.1
        self._volatility_adjustment = (alpha * ratio) + (1 - alpha) * self._volatility_adjustment
        self.logger.info(f"REGIME FEEDBACK: RelSlippage={relative_slippage:.6f}, Adj={self._volatility_adjustment:.4f}")

    def get_atr(self) -> float:
        self._ensure_computed()
        return self._current_results.get("atr", 0.0)

    def regime_score(self) -> float:
        self._ensure_computed()
        res = self._current_results
        if not res: return 0.0

        score = (0.5 * res["trend"] + 0.3 * res["efficiency"] + 0.2 * res["volatility"])
        return float(np.clip(score, 0.0, 1.0))

    def trend_strength(self) -> float:
        self._ensure_computed()
        return self._current_results.get("trend", 0.0)

    def volatility_regime(self) -> float:
        self._ensure_computed()
        return self._current_results.get("volatility", 0.5)

    def market_efficiency(self) -> float:
        self._ensure_computed()
        return self._current_results.get("efficiency", 0.0)

    def _ensure_computed(self):
        snapshot = self.market_state.get_candle_snapshot(self.symbol, self.timeframe)
        if not snapshot:
            return

        df = self.market_state.get_candles_df(self.symbol, self.timeframe)
        if df.empty:
            return

        if self._last_candle_time != snapshot.timestamp or not self._current_results:
            self._compute_regime_metrics(df, snapshot)
            self._last_candle_time = snapshot.timestamp
