from collections import deque
from typing import List

from models.liquidation import Liquidation


class LiquidationState:

    def __init__( self, max_liquidations):
        self._liquidations = deque(maxlen=max_liquidations)

    def add(self, liquidation: Liquidation):
        self._liquidations.append(liquidation)

    def get(self) -> List[Liquidation]:
        return list(self._liquidations)
