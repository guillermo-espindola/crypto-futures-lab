from collections import deque
from typing import Dict, List

from models.aggregate_trade import AggregateTrade


class AggregateTradeState:

    def __init__(self, maxlen):

        self._maxlen = maxlen
        self._data: Dict[str, deque] = {}

    def add(self, aggregate_trade: AggregateTrade):

        symbol = aggregate_trade.symbol

        if symbol not in self._data:

            self._data[symbol] = deque(
                maxlen=self._maxlen
            )

        self._data[symbol].append(aggregate_trade)

    def get(self, symbol) -> List[AggregateTrade]:

        return list(
            self._data.get(symbol, [])
        )

    def last(self, symbol):

        aggregate_trades = self.get(symbol)
        if not aggregate_trades:
            return None

        return aggregate_trades[-1]
