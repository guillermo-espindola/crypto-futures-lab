from collections import deque
from typing import Dict, List

from models.candle_event import CandleEvent
from models.candle import Candle

from utils.logger_interface import ILogger

class CandlesState:

    def __init__(self, max_candles: int, logger: ILogger):

        self._max_candles = max_candles
        self._timeframe_candles: Dict[str, deque] = {}
        self._logger = logger
        
        self.new_candle_event = CandleEvent()

    def add(self, candle: Candle):

        if candle.timeframe not in self._timeframe_candles:
            self._timeframe_candles[candle.timeframe] = deque(maxlen=self._max_candles)

        current_candles = self._timeframe_candles[candle.timeframe]

        # UPDATE LAST CANDLE
        if (len(current_candles) > 0 and current_candles[-1].open_time == candle.open_time):
            current_candles[-1] = candle

        else:
            current_candles.append(candle)
            self._logger.info(f"[ADDED] {candle}")
            self.new_candle_event.trigger(candle)

    def get_timeframe_candles(self, timeframe:str) -> List[Candle]:
        return list(self._timeframe_candles.get(timeframe, []))
