from dataclasses import dataclass

from models.position_type import PositionType

@dataclass(slots=True)
class Position:

    symbol: str

    position_type: PositionType

    entry_price: float

    quantity: float

    leverage: float

    timestamp: int

    stop_loss: float

    take_profit: float

    fees_paid: float = 0.0

    realized_pnl: float = 0.0

    def calculate_unrealized_pnl(self, current_price: float) -> float:
        if self.position_type == PositionType.LONG:
            return (current_price - self.entry_price) * self.quantity

        return (self.entry_price - current_price) * self.quantity

    # =====================================================
    # NOTIONAL
    # =====================================================

    def notional(self) -> float:
        """
        Returns the notional value of the position.
        Notional = Entry Price * Quantity
        """
        return self.entry_price * self.quantity
