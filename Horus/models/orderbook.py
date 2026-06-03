from dataclasses import dataclass
from typing import List, Tuple
import math


@dataclass(slots=True)
class OrderBook:

    symbol: str

    event_time: int

    transaction_time: int

    first_update_id: int

    final_update_id: int

    previous_update_id: int

    bids: List[Tuple[float, float]]

    asks: List[Tuple[float, float]]

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        for side in [self.bids, self.asks]:

            for price, qty in side:

                if (
                    math.isnan(price)
                    or
                    math.isinf(price)
                ):
                    raise ValueError(
                        "Invalid price"
                    )

                if qty < 0:
                    raise ValueError(
                        "Negative qty"
                    )

    # =====================================================
    # PARSER
    # =====================================================

    @staticmethod
    def from_json(data):

        orderbook = OrderBook(
            symbol=str(data["s"]),

            event_time=int(data["E"]),

            transaction_time=int(data["T"]),

            first_update_id=int(data["U"]),

            final_update_id=int(data["u"]),

            previous_update_id=int(data["pu"]),

            bids=[
                (
                    float(price),
                    float(qty)
                )
                for price, qty in data["b"]
            ],

            asks=[
                (
                    float(price),
                    float(qty)
                )
                for price, qty in data["a"]
            ]
        )

        orderbook.validate()

        return orderbook

    # =====================================================
    # BEST BID
    # =====================================================

    def best_bid(self):

        if not self.bids:
            return None

        return max(
            self.bids,
            key=lambda x: x[0]
        )

    # =====================================================
    # BEST ASK
    # =====================================================

    def best_ask(self):

        if not self.asks:
            return None

        return min(
            self.asks,
            key=lambda x: x[0]
        )