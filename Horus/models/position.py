from dataclasses import dataclass

@dataclass(slots=True)
class Position:

    symbol: str

    side: str

    entry_price: float

    quantity: float

    leverage: float

    timestamp: int

    stop_loss: float

    take_profit: float

    fees_paid: float = 0.0

    realized_pnl: float = 0.0

    # =====================================================
    # UNREALIZED
    # =====================================================

    def unrealized_pnl(
        self,
        current_price: float
    ) -> float:
        """
        Calculates the unrealized PnL based on price movement.
        PnL = (Current - Entry) * Qty for Long
        PnL = (Entry - Current) * Qty for Short
        """
        if self.side == "LONG":
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
