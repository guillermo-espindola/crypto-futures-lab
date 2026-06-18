from dataclasses import dataclass

@dataclass(frozen=True)
class HistoryConfig:
    candles_endpoint: str
    orderbook_depth_endpoint: str
    aggregate_trades_endpoint: str