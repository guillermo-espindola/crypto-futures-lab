import numpy as np

class ScoringEngine:

    def __init__(self, microstructure_engine, regime_engine):

        self.micro = microstructure_engine
        self.regime_engine = regime_engine

    # =====================================================

    def _clamp(self, value: float) -> float:
        return float(np.clip(value, 0.0, 1.0))

    # =====================================================

    def _regime(self) -> float:
        return self._clamp(self.regime_engine.regime_score())

    # =====================================================

    def _compose(self, directional: float, regime: float) -> float:

        if regime < 0.4:
            return 0.0

        if directional < 0.25:
            return 0.0

        score = (directional ** 0.6) * (regime ** 0.4)

        return self._clamp(score)

    # =====================================================

    def long_score(self) -> float:

        directional = self.micro.long_context()
        regime = self._regime()

        print(f"[LONG] dir={directional:.3f} reg={regime:.3f}")

        score = self._compose(directional, regime)

        print(f"[LONG SCORE] {score:.3f}")

        return score

    # =====================================================

    def short_score(self) -> float:

        directional = self.micro.short_context()
        regime = self._regime()

        print(f"[SHORT] dir={directional:.3f} reg={regime:.3f}")

        score = self._compose(directional, regime)

        print(f"[SHORT SCORE] {score:.3f}")

        return score
    
    """
    COMO CONECTARLO AL TRADINGLOOP

    self.microstructure_engine = MicrostructureEngine(
    structure_engine=self.structure_engine,
    liquidity_engine=self.liquidity_engine,
    order_flow_engine=self.order_flow_engine
    )

    self.scoring_engine = ScoringEngine(
    microstructure_engine=self.microstructure_engine,
    regime_engine=self.regime_engine
    )
    
    
    
    """