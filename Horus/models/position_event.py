from typing import Callable, List

from models.position import Position

class PositionEvent:
    def __init__(self):
        self._handlers: List[Callable[[Position], None]] = []
    
    def subscribe(self, handler: Callable[[Position], None]):
        self._handlers.append(handler)

    def trigger(self, position: Position):
        for handler in self._handlers:
            handler(position)
