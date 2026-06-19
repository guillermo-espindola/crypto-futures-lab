from typing import Dict

from models.aggregate_trade import AggregateTrade
from models.candle import Candle
from state.candles_state import CandlesState
from utils.logger_interface import ILogger


class CandleAggregator:

    def __init__(
        self,
        timeframe_seconds: int,
        candles_state: CandlesState,
        logger: ILogger
    ):
        self._timeframe_milliseconds = timeframe_seconds * 1000
        self._candles_state = candles_state
        self._logger = logger
        self._bucket: Dict[int, Candle] = {}

    def refresh(self, timestamp: int, current_price: float):
        pass

    def add(self, aggregate_trade: AggregateTrade):

        symbol = aggregate_trade.symbol
        timestamp = aggregate_trade.trade_time

        bucket_start_time = self._truncate_timestamp(timestamp)

        if bucket_start_time not in self._bucket:
            self._bucket[bucket_start_time] = self._init_bucket(symbol, aggregate_trade, bucket_start_time)

        self._update_bucket(self._bucket[bucket_start_time], aggregate_trade)

        self._flush(timestamp)

    def _truncate_timestamp(self, timestamp: int) -> int:
        return (timestamp // self._timeframe_milliseconds) * self._timeframe_milliseconds

    def _calculate_end_time(self, start_time: int) -> int:
        return start_time + self._timeframe_milliseconds

    def _flush(self, current_timestamp: int):

        for bucket_start_time in sorted(list(self._bucket.keys())):

            if current_timestamp < self._calculate_end_time(bucket_start_time):
                break

            candle = self._bucket[bucket_start_time]

            self._candles_state.add(candle)

            del self._bucket[bucket_start_time]

    def _init_bucket(self, symbol: str, aggregate_trade: AggregateTrade, start_time: int) -> Candle:

        return Candle(
            symbol=symbol,
            timeframe=f"{self._timeframe_milliseconds // 1000}s",

            open_time=start_time,
            close_time=self._calculate_end_time(start_time),

            open=aggregate_trade.price,
            high=aggregate_trade.price,
            low=aggregate_trade.price,
            close=aggregate_trade.price,

            volume=0.0,
            quote_asset_volume=0.0,

            trades=0,

            taker_buy_base_volume=0.0,
            taker_buy_quote_volume=0.0,

            is_closed=True
        )

    def _update_bucket(self, candle: Candle, trade: AggregateTrade):

        price = trade.price
        quantity = trade.quantity

        candle.high = max(candle.high, price)
        candle.low = min(candle.low, price)
        candle.close = price

        candle.volume += quantity
        candle.quote_asset_volume += price * quantity

        candle.trades += 1

        if not trade.is_buyer_maker:
            candle.taker_buy_base_volume += quantity
            candle.taker_buy_quote_volume += price * quantity
