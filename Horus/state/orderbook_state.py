from typing import Dict, List, Tuple, Optional

from models.orderbook import OrderBook
from models.orderbook_snapshot import OrderBookSnapshot

from utils.logger_interface import ILogger

class OrderBookState:

    def __init__(self, logger: ILogger):
        # symbol -> {"bids": {price: qty}, "asks": {price: qty}}
        self._books: Dict[str, Dict[str, Dict[float, float]]] = {}
        self._last_update_id: Dict[str, int] = {}
        self._event_times: Dict[str, int] = {}
        self._transaction_times: Dict[str, int] = {}
        self._logger = logger

    def apply_snapshot(self, symbol: str, snapshot: OrderBookSnapshot):
        bids = {float(p): float(q) for p, q in snapshot.bids}
        asks = {float(p): float(q) for p, q in snapshot.asks}

        self._books[symbol] = {
            "bids": bids,
            "asks": asks
        }
        self._last_update_id[symbol] = snapshot.final_update_id
        self._event_times[symbol] = snapshot.event_time
        self._transaction_times[symbol] = snapshot.transaction_time
        self._logger.info(f"OrderBook snapshot applied for {symbol}. ID: {snapshot.final_update_id}")

    def update(self, update: OrderBook):
        symbol = update.symbol
        if symbol not in self._books:
            self._logger.warn(f"Received update for {symbol} but no snapshot is loaded. Skipping.")
            return

        # Sequence validation (Binance: u must be >= lastUpdateId of snapshot)
        if update.previous_update_id < self._last_update_id.get(symbol, 0):
            self._logger.error(f"OrderBook update sequence gap for {symbol}. Recovery required.")
            return

        book = self._books[symbol]

        # Update Bids
        for price, qty in update.bids:
            p, q = float(price), float(qty)
            if q == 0:
                book["bids"].pop(p, None)
            else:
                book["bids"][p] = q

        # Update Asks
        for price, qty in update.asks:
            p, q = float(price), float(qty)
            if q == 0:
                book["asks"].pop(p, None)
            else:
                book["asks"][p] = q

        self._last_update_id[symbol] = update.final_update_id
        self._event_times[symbol] = update.event_time
        self._transaction_times[symbol] = update.transaction_time

    def get(self, symbol: str) -> Optional[OrderBookSnapshot]:
        """
        Returns the current local book reconstructed as an OrderBookSnapshot.
        """
        book = self._books.get(symbol)
        if not book:
            return None

        # Convert dict back to List[Tuple] for the snapshot model
        bids = sorted(book["bids"].items(), key=lambda x: x[0], reverse=True)
        asks = sorted(book["asks"].items(), key=lambda x: x[0])

        return OrderBookSnapshot(
            final_update_id=self._last_update_id.get(symbol, 0),
            event_time=self._event_times.get(symbol, 0),
            transaction_time=self._transaction_times.get(symbol, 0),
            bids=bids,
            asks=asks
        )

    def get_book(self, symbol: str) -> Optional[Dict[str, Dict[float, float]]]:
        """Returns the raw local book."""
        return self._books.get(symbol)

    def get_sorted_bids(self, symbol: str, limit: int = 20) -> List[Tuple[float, float]]:
        """Returns the top N bids sorted descending."""
        book = self._books.get(symbol)
        if not book: return []

        sorted_bids = sorted(book["bids"].items(), key=lambda x: x[0], reverse=True)
        return sorted_bids[:limit]

    def get_sorted_asks(self, symbol: str, limit: int = 20) -> List[Tuple[float, float]]:
        """Returns the top N asks sorted ascending."""
        book = self._books.get(symbol)
        if not book: return []

        sorted_asks = sorted(book["asks"].items(), key=lambda x: x[0])
        return sorted_asks[:limit]

    def exists(self, symbol: str) -> bool:
        return symbol in self._books
