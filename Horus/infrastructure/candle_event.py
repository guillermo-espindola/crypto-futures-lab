from typing import Callable, List

from models.candle import Candle

class CandleEvent:
    def __init__(self):
        self._handlers: List[Callable[[Candle], None]] = []
    
    def subscribe(self, handler: Callable[[Candle], None]):
        self._handlers.append(handler)

    def trigger(self, candle: Candle):
        for handler in self._handlers:
            handler(candle)
