import pandas as pd

from dataclasses import dataclass
from typing import List, Optional

from models.liquidation import Liquidation
from models.orderbook_snapshot import OrderBookSnapshot
from models.trade import Trade

@dataclass
class MarketSnapshot:
    symbol: str
    candles_df: pd.DataFrame
    trades: List[Trade]
    orderbook: Optional[OrderBookSnapshot]
    liquidations: List[Liquidation]
    timestamp: float