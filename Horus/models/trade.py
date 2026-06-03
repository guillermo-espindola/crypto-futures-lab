from dataclasses import dataclass
import math


@dataclass(slots=True)
class Trade:

    event_time: int
    
    trade_time: int

    symbol: str

    trade_id: int

    price: float

    quantity: float

    execution_type: str

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

        trade = Trade(
            event_time=int(data["E"]),

            trade_time=int(data["T"]),

            symbol=str(data["s"]),

            trade_id=int(data["t"]),

            price=float(data["p"]),

            quantity=float(data["q"]),

            execution_type=str(data["X"]),

            is_buyer_maker=bool(data["m"])
        )

        trade.validate()

        return trade