from dataclasses import dataclass
import math


@dataclass(slots=True)
class Liquidation:

    symbol: str

    side: str

    order_type: str

    quantity: float

    price: float

    average_price: float

    status: str

    trade_time: int

    event_time: int

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self):

        if self.quantity <= 0:
            raise ValueError(
                "Invalid quantity"
            )

        if (
            math.isnan(self.price)
            or
            math.isinf(self.price)
        ):
            raise ValueError(
                "Invalid price"
            )

    # =====================================================
    # PARSER
    # =====================================================

    @staticmethod
    def from_json(data):

        o = data["o"]

        liq = Liquidation(
            symbol=str(o["s"]),

            side=str(o["S"]),

            order_type=str(o["o"]),

            quantity=float(o["q"]),

            price=float(o["p"]),

            average_price=float(o["ap"]),

            status=str(o["X"]),

            trade_time=int(o["T"]),

            event_time=int(data["E"])
        )

        liq.validate()

        return liq