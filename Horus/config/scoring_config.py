from dataclasses import dataclass

@dataclass(frozen=True)
class ScoringConfig:
    ema_alpha: float
    confirmation_threshold: int
    long_bias_weight: float
    flow_weight: float
    regime_weight: float
    book_weight: float