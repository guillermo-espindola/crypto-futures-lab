from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class MarketConfig:
    symbol: str
    timeframe: str
    timeframes: List[str]
    timeframe_seconds: int
    timer_seconds: int
    max_candles: int
    max_agg_trades: int
    max_liquidations: int
    max_trades:int
    max_orderbook_depth: int   