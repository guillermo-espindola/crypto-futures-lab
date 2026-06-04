from dataclasses import dataclass

from models.position_type import PositionType

@dataclass(slots=True)
class Position:

    position_type: PositionType

    entry_price: float

    quantity: float

    leverage: float

    timestamp: int

    stop_loss: float

    take_profit: float

    total_fees_paid: float = 0.0

    realized_pnl: float = 0.0

    def calculate_pnl(self, current_price: float) -> float:
        if self.position_type == PositionType.LONG:
            return (current_price - self.entry_price) * self.quantity
        return (self.entry_price - current_price) * self.quantity

    def calculate_notional(self) -> float:
        return self.entry_price * self.quantity
