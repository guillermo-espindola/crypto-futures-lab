from collections import deque
from typing import Dict, List

from models.aggregate_trade import AggregateTrade


class AggregateTradeState:

    def __init__(
        self,
        maxlen=10000
    ):

        self.maxlen = maxlen

        self.data: Dict[
            str,
            deque
        ] = {}

    # =====================================================
    # ADD
    # =====================================================

    def add(
        self,
        aggregate_trade: AggregateTrade
    ):

        symbol = aggregate_trade.symbol

        if symbol not in self.data:

            self.data[symbol] = deque(
                maxlen=self.maxlen
            )

        self.data[symbol].append(aggregate_trade)

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        symbol
    ) -> List[AggregateTrade]:

        return list(
            self.data.get(symbol, [])
        )

    # =====================================================
    # LAST
    # =====================================================

    def last(
        self,
        symbol
    ):

        aggregate_trades = self.get(symbol)

        if not aggregate_trades:
            return None

        return aggregate_trades[-1]