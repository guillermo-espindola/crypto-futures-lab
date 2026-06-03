from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass(frozen=True)
class OrderBookSnapshot:
    """
    Represents a full order book snapshot from the Binance REST API
    or a reconstructed state of the local order book.
    """
    final_update_id: int
    event_time: int
    transaction_time: int
    bids: List[Tuple[float, float]]
    asks: List[Tuple[float, float]]

    @classmethod
    def from_json(cls, data: dict) -> 'OrderBookSnapshot':
        # Binance REST API for depth uses 'lastUpdateId', 'E', 'T', 'bids', 'asks'
        return cls(
            final_update_id=int(data["lastUpdateId"]),
            event_time=int(data["E"]),
            transaction_time=int(data["T"]),
            bids=[(float(p), float(q)) for p, q in data["bids"]],
            asks=[(float(p), float(q)) for p, q in data["asks"]],
        )

    def best_bid(self) -> Optional[Tuple[float, float]]:
        """Returns the highest bid (top of the book)."""
        return self.bids[0] if self.bids else None

    def best_ask(self) -> Optional[Tuple[float, float]]:
        """Returns the lowest ask (top of the book)."""
        return self.asks[0] if self.asks else None
