from dataclasses import dataclass, field
from typing import Dict, Optional
from models.position import Position
from models.portfolio_snapshot import PortfolioSnapshot

class PortfolioEngine:
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions: list[Position] = []
        self.realized_pnl = 0.0
        self.fees_paid = 0.0

    def open_position(self, position: Position):
        self.positions.append(position)
        # Fees are deducted from balance immediately upon opening
        self.balance -= position.fees_paid
        self.fees_paid += position.fees_paid
        return True

    def close_position(self, position: Position, exit_price: float) -> Optional[float]:
        if position not in self.positions:
            return None

        self.positions.remove(position)

        # Calculate final PnL for this trade
        pnl = position.unrealized_pnl(exit_price)

        # Update global account state
        self.realized_pnl += pnl
        self.balance += pnl
        return pnl

    def equity(self, mark_prices: Dict[str, float]) -> float:
        """
        Equity = Liquid Balance + Sum of Unrealized PnL of all open positions.
        """
        unrealized = 0.0
        for position in self.positions:
            price = mark_prices.get(position.symbol)
            if price:
                unrealized += position.unrealized_pnl(price)

        return self.balance + unrealized

    def exposure(self) -> float:
        return sum(p.notional() for p in self.positions)

    def snapshot(self, mark_prices: Dict[str, float], timestamp: int) -> PortfolioSnapshot:
        equity = self.equity(mark_prices)
        return PortfolioSnapshot(
            timestamp=timestamp,
            balance=self.balance,
            equity=equity,
            margin_used=self.exposure(),
            unrealized_pnl=equity - self.balance,
            realized_pnl=self.realized_pnl,
            exposure=self.exposure(),
            open_positions=len(self.positions)
        )
