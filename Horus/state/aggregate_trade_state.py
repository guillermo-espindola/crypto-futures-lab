from collections import deque
from typing import List

from models.aggregate_trade import AggregateTrade


class AggregateTradeState:

    def __init__(self, max_aggregate_trades):

        self._max_aggregate_trades = max_aggregate_trades
        self._aggregate_trades = deque(maxlen=max_aggregate_trades)

    def add(self, aggregate_trade: AggregateTrade):
        self._aggregate_trades.append(aggregate_trade)

    def get(self) -> List[AggregateTrade]:
        return list(self._aggregate_trades)