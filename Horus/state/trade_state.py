from collections import deque
from typing import Dict, List

from models.trade import Trade


class TradeState:

    def __init__(self, maxlen):
        self._maxlen = maxlen
        self._data: Dict[str, deque] = {}

    def add(self, trade: Trade):

        symbol = trade.symbol

        if symbol not in self._data:

            self._data[symbol] = deque(
                maxlen=self._maxlen
            )

        self._data[symbol].append(trade)

    def get(self, symbol) -> List[Trade]:

        return list(
            self._data.get(symbol, [])
        )
    

    def last(self, symbol):

        trades = self.get(symbol)

        if not trades:
            return None

        return trades[-1]
