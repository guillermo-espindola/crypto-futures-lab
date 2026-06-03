from dataclasses import dataclass


@dataclass(init=True)
class StateSnapshot:

    timestamp: int

    symbol: str

    candles_1m: int
    candles_5m: int
    candles_15m: int
    candles_1h: int

    trades: int

    liquidations: int

    has_orderbook: bool