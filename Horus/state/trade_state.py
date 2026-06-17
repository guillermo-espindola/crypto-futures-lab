from collections import deque
from typing import List

from models.trade import Trade

class TradeState:

    def __init__(self, max_trades):
        self._current_trades= deque(maxlen=max_trades)

    def add(self, trade: Trade):
        self._current_trades.append(trade)

    def get_current_trades(self) -> List[Trade]:
        return list(self._current_trades)
