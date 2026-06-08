from collections import deque
from typing import Dict, List

from models.liquidation import Liquidation


class LiquidationState:

    def __init__( self, maxlen):
        self._maxlen = maxlen
        self._data: Dict[str, deque] = {}

    def add(self, liquidation: Liquidation):

        symbol = liquidation.symbol

        if symbol not in self._data:

            self._data[symbol] = deque(
                maxlen=self._maxlen
            )

        self._data[symbol].append(
            liquidation
        )

    def get(self, symbol) -> List[Liquidation]:

        return list(
            self._data.get(symbol, [])
        )

    def last(self, symbol):

        liqs = self.get(symbol)

        if not liqs:
            return None

        return liqs[-1]
