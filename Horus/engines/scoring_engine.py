import numpy as np
from typing import Tuple
from config.config_manager import ConfigManager
from utils.logger import Logger
from engines.structure_engine import StructureEngine
from engines.liquidity_engine import LiquidityEngine
from engines.order_flow_engine import OrderFlowEngine
from engines.regime_engine import RegimeEngine
from engines.order_book_engine import OrderBookEngine

class ScoringEngine:
    """
    Calibrated Scoring Engine
    ------------------------
    Fuses market structure, liquidity, order flow and regime into a
    probabilistic signal [0.0 -> 1.0].

    Implements a calibration layer to normalize signals across different regimes.
    """

    def __init__(self,
                 structure_engine: StructureEngine,
                 liquidity_engine: LiquidityEngine,
                 order_flow_engine: OrderFlowEngine,
                 regime_engine: RegimeEngine,
                 order_book_engine: OrderBookEngine,
                 config_manager: ConfigManager,
                 logger: Logger):
        self._structure_engine = structure_engine
        self._liquidity_engine = liquidity_engine
        self._order_flow_engine = order_flow_engine
        self._regime_engine = regime_engine
        self._order_book_engine = order_book_engine
        self._logger = logger
        self._config_manager = config_manager

    def _sigmoid(self, x: float) -> float:
        # Numerical stability for sigmoid
        if x < -709: return 0.0
        if x > 709: return 1.0
        return 1 / (1 + np.exp(-x))

    def _calibrate(self, raw_score: float, regime_multiplier: float) -> float:
        """
        Calibrates raw score using a sigmoid function scaled by regime quality.
        The center is 0.5 (neutral).
        """
        # Center the score around 0 for the sigmoid.
        # If raw_score is 0.5, normalized is 0, sigmoid(0) = 0.5.
        # regime_multiplier increases the steepness (confidence).
        normalized = (raw_score - 0.5) * 10 * regime_multiplier
        return self._sigmoid(normalized)

    def compute_scores(self) -> Tuple[float, float]:
        """
        Single-pass computation of both long and short scores to avoid redundancy.
        """
        # 1. Get context from RegimeEngine (which uses the cached CandleSnapshot)
        atr = self._regime_engine.get_atr()
        regime_val = self._regime_engine.regime_score()

        # 2. Weights from config (driven by the active mode)
        w_struct = self._config_manager.get_config().scoring.long_bias_weight
        w_flow = self._config_manager.get_config().scoring.long_bias_weight
        w_regime = self._config_manager.get_config().scoring.regime_weight
        w_book = self._config_manager.get_config().scoring.book_weight

        # 3. Long Components
        struct_long = self._structure_engine.bos_up(atr)
        liq_long = self._liquidity_engine.sweep_low(atr)
        flow_long = self._order_flow_engine.get_absorption_buy()
        book_long = self._order_book_engine.calculate_imbalance() # [-1, 1]

        # Convert book imbalance [-1, 1] to [0, 1] for the weighted sum
        book_long_norm = (book_long + 1.0) / 2.0

        # Structure and Liquidity are combined into a bias
        bias_long = (0.7 * struct_long) + (0.3 * liq_long)

        # 4. Short Components
        struct_short = self._structure_engine.bos_down(atr)
        liq_short = self._liquidity_engine.sweep_high(atr)
        flow_short = self._order_flow_engine.get_absorption_sell()
        book_short = -self._order_book_engine.calculate_imbalance() # Inverse of long imbalance

        book_short_norm = (book_short + 1.0) / 2.0

        bias_short = (0.7 * struct_short) + (0.3 * liq_short)

        # 5. Fusion (Weighted Sum)
        # We include the normalized order book pressure in the fusion
        raw_long = (w_struct * bias_long) + (w_flow * flow_long) + (w_regime * regime_val) + (w_book * book_long_norm)
        raw_short = (w_struct * bias_short) + (w_flow * flow_short) + (w_regime * regime_val) + (w_book * book_short_norm)

        # 6. Calibration Layer
        # Final score is a probabilistic output [0, 1]
        final_long = self._calibrate(raw_long, regime_val)
        final_short = self._calibrate(raw_short, regime_val)

        self._logger.info(f"[SCORING] Regime: {regime_val:.2f}, OB_Imbalance: {book_long:.2f}")
        self._logger.info(f"[SCORING] Long: {final_long:.4f} (raw:{raw_long:.2f})")
        self._logger.info(f"[SCORING] Short: {final_short:.4f} (raw:{raw_short:.2f})")

        return float(np.clip(final_long, 0.0, 1.0)), float(np.clip(final_short, 0.0, 1.0))

    def long_score(self) -> float:
        return self.compute_scores()[0]

    def short_score(self) -> float:
        return self.compute_scores()[1]
