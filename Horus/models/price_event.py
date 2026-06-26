from typing import List, Callable

class PriceEvent:
    def __init__(self):
        self._callbacks: List[Callable[[float], None]] = []
    
    def subscribe(self, callback: Callable[[float], None]):
        self._callbacks.append(callback)
    
    def trigger(self, price: float):
        for callback in self._callbacks:
            callback(price)