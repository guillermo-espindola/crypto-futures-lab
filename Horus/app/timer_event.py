from typing import Callable, List

from models.candle import Candle

class TimerEvent:
    def __init__(self):
        self._handlers: List[Callable[[int], None]] = []
    
    def subscribe(self, handler: Callable[[int], None]):
        self._handlers.append(handler)

    def trigger(self, timestamp: int):
        for handler in self._handlers:
            handler(timestamp)
