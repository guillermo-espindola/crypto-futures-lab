from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioSnapshot:

    timestamp: int

    balance: float

    equity: float

    margin_used: float

    unrealized_pnl: float

    realized_pnl: float

    exposure: float

    open_positions: int