from dataclasses import dataclass

@dataclass(slots=True)
class AggregateTradeSnapshot:

    aggregate_trade_id: int

    price: float

    quantity: float

    normal_quantity: float

    first_trade_id: int

    last_trade_id: int

    timestamp: int

    is_buyer_maker: bool

    # =====================================================
    # PARSER
    # =====================================================

    @staticmethod
    def from_json(data):

        aggregate_trade_snapshot = AggregateTradeSnapshot(

            aggregate_trade_id=int(data["a"]),

            price=float(data["p"]),

            quantity=float(data["q"]),

            normal_quantity=float(data["nq"]),

            first_trade_id=int(data["f"]),

            last_trade_id=int(data["l"]),

            timestamp=int(data["T"]),

            is_buyer_maker=bool(data["m"])
        )

        return aggregate_trade_snapshot