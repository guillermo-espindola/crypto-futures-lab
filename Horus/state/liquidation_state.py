from collections import deque
from typing import Dict, List

from models.liquidation import Liquidation


class LiquidationState:

    def __init__(
        self,
        maxlen=5000
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
        liquidation: Liquidation
    ):

        symbol = liquidation.symbol

        if symbol not in self.data:

            self.data[symbol] = deque(
                maxlen=self.maxlen
            )

        self.data[symbol].append(
            liquidation
        )

    # =====================================================
    # GET
    # =====================================================

    def get(
        self,
        symbol
    ) -> List[Liquidation]:

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

        liqs = self.get(symbol)

        if not liqs:
            return None

        return liqs[-1]