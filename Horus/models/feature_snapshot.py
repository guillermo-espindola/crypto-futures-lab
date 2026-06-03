from dataclasses import dataclass


@dataclass(slots=True)
class FeatureSnapshot:

    timestamp: int

    symbol: str

    timeframe: str

    orderbook_imbalance: float

    delta: float

    cumulative_delta: float

    spread: float

    volatility: float

    trend_strength: float

    liquidity_score: float

    liquidation_pressure: float

    long_probability: float

    short_probability: float