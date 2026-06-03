from dataclasses import dataclass
from typing import Dict, Any
import math


@dataclass(slots=True)
class Candle:

    symbol: str
    timeframe: str

    open_time: int
    close_time: int

    open: float
    high: float
    low: float
    close: float

    volume: float

    quote_asset_volume: float

    trades: int

    taker_buy_base_volume: float
    taker_buy_quote_volume: float

    is_closed: bool

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        prices = [
            self.open,
            self.high,
            self.low,
            self.close
        ]

        for value in prices:

            if (
                math.isnan(value)
                or
                math.isinf(value)
            ):
                raise ValueError(
                    "Invalid candle price"
                )

            if value <= 0:
                raise ValueError(
                    "Price must be > 0"
                )

        if self.high < self.low:
            raise ValueError(
                "High < Low"
            )

        if self.volume < 0:
            raise ValueError(
                "Negative volume"
            )

    # =====================================================
    # PARSER
    # =====================================================

    @staticmethod
    def from_json(data: Dict[str, Any]):

        k = data["k"]

        candle = Candle(
            symbol=str(k["s"]),
            timeframe=str(k["i"]),

            open_time=int(k["t"]),
            close_time=int(k["T"]),

            open=float(k["o"]),
            high=float(k["h"]),
            low=float(k["l"]),
            close=float(k["c"]),

            volume=float(k["v"]),

            quote_asset_volume=float(k["q"]),

            trades=int(k["n"]),

            taker_buy_base_volume=float(k["V"]),
            taker_buy_quote_volume=float(k["Q"]),

            is_closed=bool(k["x"])
        )

        candle.validate()

        return candle

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(self):

        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,

            "open_time": self.open_time,
            "close_time": self.close_time,

            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,

            "volume": self.volume,

            "quote_asset_volume":
                self.quote_asset_volume,

            "trades": self.trades,

            "taker_buy_base_volume":
                self.taker_buy_base_volume,

            "taker_buy_quote_volume":
                self.taker_buy_quote_volume,

            "is_closed": self.is_closed
        }