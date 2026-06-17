from typing import List, Tuple, Optional

from models.orderbook_depth_update import OrderBookDepthUpdate
from models.orderbook import OrderBook

from utils.logger_interface import ILogger

class OrderBookState:

    def __init__(self, logger: ILogger):
        self._current_orderbook: OrderBook = None
        self._logger = logger

    def set_orderbook(self, orderbook: OrderBook):
        self._current_orderbook = orderbook

    def update(self, depthUpdate: OrderBookDepthUpdate):

        if not self._current_orderbook:
            self._logger.error(f"Received update for {depthUpdate} but no orderbook is loaded. Skipping.")
            return
        
        if depthUpdate.previous_update_id < self._current_orderbook.last_update_id:
            self._logger.error(f"OrderBook update sequence gap. Recovery required.")
            return
        
        # Update Bids
        for price, quantity in depthUpdate.bids.items():
            if quantity == 0:
                self._current_orderbook.bids.pop(price, None)
            else:
                self._current_orderbook.bids[price] = quantity

        # Update Asks
        for price, quantity in depthUpdate.asks.items():
            p, q = float(price), float(quantity)
            if quantity == 0:
                self._current_orderbook.asks.pop(price, None)
            else:
                self._current_orderbook.asks[price] = quantity

    def get_orderbook(self) -> Optional[OrderBook]:
        return self._current_orderbook

    def get_sorted_bids(self, limit: int = 20) -> List[Tuple[float, float]]:
        if not self._current_orderbook:
            return []

        sorted_bids = sorted(self._current_orderbook.bids.items(), reverse=True)
        return sorted_bids[:limit]

    def get_sorted_asks(self, limit: int = 20) -> List[Tuple[float, float]]:
        if not self._current_orderbook:
            return []
        sorted_asks = sorted(self._current_orderbook.asks.items())
        return sorted_asks[:limit]
    
