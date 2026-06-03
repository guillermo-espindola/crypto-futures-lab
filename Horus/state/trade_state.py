from collections import deque
from typing import Dict, List

from models.trade import Trade


class TradeState:

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
        trade: Trade
    ):

        symbol = trade.symbol

        if symbol not in self.data:

            self.data[symbol] = deque(
                maxlen=self.maxlen
            )

        self.data[symbol].append(trade)

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        symbol
    ) -> List[Trade]:

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

        trades = self.get(symbol)

        if not trades:
            return None

        return trades[-1]