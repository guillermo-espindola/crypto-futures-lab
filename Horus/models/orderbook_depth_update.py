from dataclasses import dataclass

@dataclass(slots=True)
class OrderBookDepthUpdate:

    symbol: str

    event_time: int

    transaction_time: int

    first_update_id: int

    final_update_id: int

    previous_update_id: int

    bids: dict[float, float]

    asks: dict[float, float]

    @staticmethod
    def from_json(data):

        bids: dict[float, float] = {}
        asks: dict[float, float] = {}

        for price, quantity in data["b"]:
            bids[float(price)] = float(quantity)
        
        for price, quantity in data["a"]:
            asks[float(price)] = float(quantity)

        orderbook_depth_update = OrderBookDepthUpdate(
            symbol=str(data["s"]),

            event_time=int(data["E"]),

            transaction_time=int(data["T"]),

            first_update_id=int(data["U"]),

            final_update_id=int(data["u"]),

            previous_update_id=int(data["pu"]),

            bids=bids,

            asks=asks
        )

        return orderbook_depth_update
