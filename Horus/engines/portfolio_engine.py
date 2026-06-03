from typing import Dict, Optional
from models.position import Position
from models.portfolio_snapshot import PortfolioSnapshot

class PortfolioEngine:
    def __init__(self, initial_balance: float):
        self._balance = initial_balance
        self._positions: list[Position] = []
        self._realized_pnl = 0.0

    def open_position(self, position: Position):
        self._positions.append(position)
        self._balance -= position.fees_paid
        return True

    def close_position(self, position: Position, exit_price: float) -> Optional[float]:
        if position not in self._positions:
            return None

        self._positions.remove(position)

        pnl = position.calculate_unrealized_pnl(exit_price)

        # Update global account state
        self._realized_pnl += pnl
        self._balance += pnl
        return pnl

    def equity(self, mark_prices: Dict[str, float]) -> float:
        """
        Equity = Liquid Balance + Sum of Unrealized PnL of all open positions.
        """
        unrealized = 0.0
        for position in self._positions:
            price = mark_prices.get(position.symbol)
            if price:
                unrealized += position.calculate_unrealized_pnl(price)

        return self._balance + unrealized

    def exposure(self) -> float:
        return sum(p.notional() for p in self._positions)

    def snapshot(self, mark_prices: Dict[str, float], timestamp: int) -> PortfolioSnapshot:
        equity = self.equity(mark_prices)
        return PortfolioSnapshot(
            timestamp=timestamp,
            balance=self._balance,
            equity=equity,
            margin_used=self.exposure(),
            unrealized_pnl=equity - self._balance,
            realized_pnl=self._realized_pnl,
            exposure=self.exposure(),
            open_positions=len(self._positions)
        )
