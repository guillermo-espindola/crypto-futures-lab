from dataclasses import dataclass

@dataclass(frozen=True)
class LiquidityConfig:
    lookback_period: int
    sweep_sensitivity: float