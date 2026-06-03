from dataclasses import dataclass

@dataclass(frozen=True)
class CandleSnapshot:
    """
    Immutable snapshot of candle-based features for a specific symbol and timeframe.
    Used to synchronize all macro-engines and eliminate redundant calculations.
    """
    symbol: str
    timeframe: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    atr: float
    is_closed: bool
