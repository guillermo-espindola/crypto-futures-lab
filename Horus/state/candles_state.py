from collections import deque
from infrastructure.candle_event import CandleEvent
from models.candle import Candle
from typing import Dict, List, Optional
from utils.logger_interface import ILogger

class CandlesState:

    def __init__(self, max_length: int, logger: ILogger):

        self._max_length = max_length
        self._candles_data: Dict[str, Dict[str, deque]] = {}
        self._logger = logger
        self.candle_event = CandleEvent()

    def add(self, candle: Candle):

        if candle.symbol not in self._candles_data:
            self._candles_data[candle.symbol] = {}

        if candle.timeframe not in self._candles_data[candle.symbol]:
            self._candles_data[candle.symbol][candle.timeframe] = deque(maxlen=self._max_length)

        current_candles = self._candles_data[candle.symbol][candle.timeframe]

        # UPDATE LAST CANDLE
        if (len(current_candles) > 0 and current_candles[-1].open_time == candle.open_time):
            current_candles[-1] = candle

        else:
            current_candles.append(candle)
            self._logger.info(f"Added new candle: {candle.symbol} {candle.timeframe} {candle.open_time}")
            self.candle_event.trigger(candle)

    def get(self, symbol: str, timeframe:str) -> List[Candle]:

        return list(self._candles_data.get(symbol, {}).get(timeframe, []))

    def last(self, symbol: str, timeframe: str) -> Optional[Candle]:
        current_candles = self.get(symbol, timeframe)

        if not current_candles:
            return None

        return current_candles[-1]
