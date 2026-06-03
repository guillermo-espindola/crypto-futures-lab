from dataclasses import dataclass
import math


@dataclass(slots=True)
class AggregateTrade:

    event_time: int

    symbol: str

    aggregate_trade_id: int

    price: float

    quantity: float

    first_trade_id: int

    last_trade_id: int

    trade_time: int

    is_buyer_maker: bool

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        if (
            math.isnan(self.price)
            or
            math.isinf(self.price)
        ):
            raise ValueError(
                "Invalid price"
            )

        if self.quantity <= 0:
            raise ValueError(
                "Quantity <= 0"
            )

    # =====================================================
    # PARSER
    # =====================================================

    @staticmethod
    def from_json(data):

        aggregate_trade = AggregateTrade(
            event_time=int(data["E"]),

            symbol=str(data["s"]),

            aggregate_trade_id=int(data["a"]),

            price=float(data["p"]),

            quantity=float(data["q"]),

            first_trade_id=int(data["f"]),

            last_trade_id=int(data["l"]),

            trade_time=int(data["T"]),

            is_buyer_maker=bool(data["m"])
        )

        aggregate_trade.validate()

        return aggregate_trade