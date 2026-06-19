from typing import Dict

from models.aggregate_trade import AggregateTrade
from models.candle import Candle
from state.candles_state import CandlesState
from utils.logger_interface import ILogger


class CandleAggregator:

    def __init__(
        self,
        symbol: str,
        timeframe_seconds: int,
        candles_state: CandlesState,
        logger: ILogger
    ):
        self._symbol = symbol
        self._timeframe = f"{timeframe_seconds}s"
        self._timeframe_milliseconds = timeframe_seconds * 1000
        self._candles_state = candles_state
        self._logger = logger
        self._bucket: Dict[int, Candle] = {}
        self._last_flushed_bucket_start_time: int | None = None

    def refresh(self, timestamp: int, current_price: float):

        if current_price <= 0.0:
            return

        current_bucket_start_time = self._truncate_timestamp(timestamp)

        if self._last_flushed_bucket_start_time is not None:
            next_expected = self._last_flushed_bucket_start_time + self._timeframe_milliseconds

            if current_bucket_start_time > next_expected:
                last_candle = self._candles_state.get_last(self._timeframe)
                previous_close_price = last_candle.close if last_candle is not None else None

                if previous_close_price is None and self._last_flushed_bucket_start_time in self._bucket:
                    previous_close_price = self._bucket[self._last_flushed_bucket_start_time].close

                if previous_close_price is None or previous_close_price <= 0.0:
                    previous_close_price = current_price

                if previous_close_price > 0.0:
                    fill_time = next_expected
                    while fill_time < current_bucket_start_time:
                        empty_candle = self._init_bucket_flat(
                            self._symbol,
                            fill_time,
                            previous_close_price
                        )
                        self._candles_state.add(empty_candle)
                        self._last_flushed_bucket_start_time = fill_time
                        fill_time += self._timeframe_milliseconds

        for bucket_start_time in sorted(list(self._bucket.keys())):

            if timestamp < self._calculate_end_time(bucket_start_time):
                break

            candle = self._bucket[bucket_start_time]
            self._candles_state.add(candle)
            self._last_flushed_bucket_start_time = bucket_start_time
            del self._bucket[bucket_start_time]

        if current_bucket_start_time not in self._bucket:
            open_price = current_price
            if self._last_flushed_bucket_start_time in self._bucket:
                open_price = self._bucket[self._last_flushed_bucket_start_time].close
            elif self._last_flushed_bucket_start_time is not None:
                last_candle = self._candles_state.get_last(self._timeframe)
                state_close_price = last_candle.close if last_candle is not None else None
                if state_close_price is not None and state_close_price > 0.0:
                    open_price = state_close_price

            if open_price > 0.0 and current_price > 0.0:
                self._bucket[current_bucket_start_time] = Candle(
                    symbol=self._symbol,
                    timeframe=self._timeframe,
                    open_time=current_bucket_start_time,
                    close_time=self._calculate_end_time(current_bucket_start_time),
                    open=open_price,
                    high=open_price,
                    low=open_price,
                    close=current_price,
                    volume=0.0,
                    quote_asset_volume=0.0,
                    trades=0,
                    taker_buy_base_volume=0.0,
                    taker_buy_quote_volume=0.0,
                    is_closed=True
                )
        else:
            candle = self._bucket[current_bucket_start_time]
            candle.high = max(candle.high, current_price)
            candle.low = min(candle.low, current_price)
            candle.close = current_price

    def add(self, aggregate_trade: AggregateTrade):

        symbol = aggregate_trade.symbol
        timestamp = aggregate_trade.trade_time

        if aggregate_trade.price <= 0.0:
            return

        self._flush(timestamp)

        bucket_start_time = self._truncate_timestamp(timestamp)

        if bucket_start_time not in self._bucket:
            self._bucket[bucket_start_time] = self._init_bucket(symbol, aggregate_trade, bucket_start_time)
        else:
            self._update_bucket(self._bucket[bucket_start_time], aggregate_trade)

    def _truncate_timestamp(self, timestamp: int) -> int:
        return (timestamp // self._timeframe_milliseconds) * self._timeframe_milliseconds

    def _calculate_end_time(self, start_time: int) -> int:
        return start_time + self._timeframe_milliseconds

    def _flush(self, current_timestamp: int):

        current_bucket_start_time = self._truncate_timestamp(current_timestamp)

        if self._last_flushed_bucket_start_time is not None:
            next_expected = self._last_flushed_bucket_start_time + self._timeframe_milliseconds

            if current_bucket_start_time > next_expected:
                last_candle = self._candles_state.get_last(self._timeframe)
                previous_close_price = last_candle.close if last_candle is not None else None

                if previous_close_price is None and self._last_flushed_bucket_start_time in self._bucket:
                    previous_close_price = self._bucket[self._last_flushed_bucket_start_time].close

                if previous_close_price is not None and previous_close_price > 0.0:
                    fill_time = next_expected
                    while fill_time < current_bucket_start_time:
                        empty_candle = self._init_bucket_flat(
                            self._symbol,
                            fill_time,
                            previous_close_price
                        )
                        self._candles_state.add(empty_candle)
                        self._last_flushed_bucket_start_time = fill_time
                        fill_time += self._timeframe_milliseconds

        for bucket_start_time in sorted(list(self._bucket.keys())):

            if current_timestamp < self._calculate_end_time(bucket_start_time):
                break

            candle = self._bucket[bucket_start_time]
            self._candles_state.add(candle)
            self._last_flushed_bucket_start_time = bucket_start_time
            del self._bucket[bucket_start_time]

    def _init_bucket(self, symbol: str, aggregate_trade: AggregateTrade, start_time: int) -> Candle:

        return Candle(
            symbol=symbol,
            timeframe=self._timeframe,

            open_time=start_time,
            close_time=self._calculate_end_time(start_time),

            open=aggregate_trade.price,
            high=aggregate_trade.price,
            low=aggregate_trade.price,
            close=aggregate_trade.price,

            volume=aggregate_trade.quantity,
            quote_asset_volume=aggregate_trade.price * aggregate_trade.quantity,

            trades=1,

            taker_buy_base_volume=0.0 if aggregate_trade.is_buyer_maker else aggregate_trade.quantity,
            taker_buy_quote_volume=0.0 if aggregate_trade.is_buyer_maker else aggregate_trade.price * aggregate_trade.quantity,

            is_closed=True
        )

    def _init_bucket_flat(self, symbol: str, start_time: int, price: float) -> Candle:

        return Candle(
            symbol=symbol,
            timeframe=self._timeframe,

            open_time=start_time,
            close_time=self._calculate_end_time(start_time),

            open=price,
            high=price,
            low=price,
            close=price,

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
