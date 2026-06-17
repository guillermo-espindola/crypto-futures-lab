from dataclasses import dataclass

@dataclass(frozen=True)
class OrderBook:
    
    last_update_id: int
    
    event_time: int
    
    transaction_time: int
    
    bids: dict[float, float]
    
    asks: dict[float, float]

    @staticmethod
    def from_json(data: dict) -> OrderBook:

        bids: dict[float, float] = {}
        asks: dict[float, float] = {}
        for price, quantity in data["bids"]:
            bids[float(price)] = float(quantity)
        
        for price, quantity in data["asks"]:
            asks[float(price)] = float(quantity)
        
        orderbook = OrderBook(
            last_update_id=int(data["lastUpdateId"]),
            event_time=int(data["E"]),
            transaction_time=int(data["T"]),
            bids=bids,
            asks=asks,
        )

        return orderbook
