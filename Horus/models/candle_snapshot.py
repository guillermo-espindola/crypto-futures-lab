from dataclasses import dataclass

@dataclass(frozen=True)
class CandleSnapshot:
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
