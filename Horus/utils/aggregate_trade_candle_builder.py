from collections import defaultdict
from typing import Dict

from models.aggregate_trade import AggregateTrade
from models.candle import Candle
from state.candles_state import CandlesState
from utils.logger_interface import ILogger


class AggregateTradeCandleBuilder:

    def __init__(
        self,
        timeframe_seconds: int,
        candles_state: CandlesState,
        logger: ILogger
    ):
        self._tf_ms = timeframe_seconds * 1000
        self._candles_state = candles_state
        self._logger = logger
        self._buckets: Dict[str, Dict[int, dict]] = defaultdict(dict)

    def add(self, trade: AggregateTrade):

        symbol = trade.symbol
        ts = trade.trade_time

        bucket_start = self._bucket_start(ts)
        buckets = self._buckets[symbol]

        if bucket_start not in buckets:
            buckets[bucket_start] = self._init_bucket(trade, bucket_start)

        self._update_bucket(buckets[bucket_start], trade)

        self._flush(symbol, ts)

    def _bucket_start(self, ts: int) -> int:
        return (ts // self._tf_ms) * self._tf_ms

    def _bucket_end(self, start: int) -> int:
        return start + self._tf_ms

    def _flush(self, symbol: str, current_ts: int):

        buckets = self._buckets[symbol]

        for bucket_start in sorted(list(buckets.keys())):

            if current_ts < self._bucket_end(bucket_start):
                break

            bucket = buckets[bucket_start]

            candle = self._build_candle(symbol, bucket_start, bucket)

            self._candles_state.add(candle)

            del buckets[bucket_start]

    def _init_bucket(self, trade: AggregateTrade, start: int) -> dict:

        return {
            "open_time": start,
            "close_time": start + self._tf_ms,

            "open": trade.price,
            "high": trade.price,
            "low": trade.price,
            "close": trade.price,

            "volume": trade.quantity,
            "quote_volume": trade.price * trade.quantity,

            "trades": 1,

            "taker_buy_base_volume": trade.quantity if not trade.is_buyer_maker else 0.0,
            "taker_buy_quote_volume": trade.price * trade.quantity if not trade.is_buyer_maker else 0.0,
        }

    def _update_bucket(self, bucket: dict, trade: AggregateTrade):

        price = trade.price
        qty = trade.quantity

        bucket["high"] = max(bucket["high"], price)
        bucket["low"] = min(bucket["low"], price)
        bucket["close"] = price

        bucket["volume"] += qty
        bucket["quote_volume"] += price * qty

        bucket["trades"] += 1

        if not trade.is_buyer_maker:
            bucket["taker_buy_base_volume"] += qty
            bucket["taker_buy_quote_volume"] += price * qty

    def _build_candle(self, symbol: str, start: int, b: dict) -> Candle:

        return Candle(
            symbol=symbol,
            timeframe=f"{self._tf_ms // 1000}s",

            open_time=b["open_time"],
            close_time=b["close_time"],

            open=b["open"],
            high=b["high"],
            low=b["low"],
            close=b["close"],

            volume=b["volume"],
            quote_asset_volume=b["quote_volume"],

            trades=b["trades"],

            taker_buy_base_volume=b["taker_buy_base_volume"],
            taker_buy_quote_volume=b["taker_buy_quote_volume"],

            is_closed=True
        )