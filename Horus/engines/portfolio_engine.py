from datetime import datetime
from typing import Optional
from models.position import Position
from models.portfolio_snapshot import PortfolioSnapshot
from models.position_event import PositionEvent
from utils.logger_interface import ILogger

class PortfolioEngine:
    def __init__(self, initial_balance: float,
                 logger: ILogger):
        self._balance = initial_balance
        self._realized_pnl = 0.0
        self._current_position: Optional[Position] = None
        self._logger = logger

        self.open_position_event = PositionEvent()
        self.close_position_event = PositionEvent()

    def has_open_position(self) -> bool:
        return self._current_position is not None
    
    def get_current_position(self) -> Optional[Position]:
        return self._current_position
    
    def get_balance(self) -> float:
        return self._balance
    
    def open_position(self, position: Position) -> None:
        assert not self.has_open_position(), "Portfolio already has an open position"
        self._balance -= position.total_fees_paid
        self._current_position = position
        self._logger.info(f"[OPEN {position.position_type.value}] Q={position.quantity:.4f} P={position.entry_price:.6f} " 
                          f"TP={position.take_profit:.6f} SL={position.stop_loss:.6f} TP={position.take_profit:.6f} ")
        self.open_position_event.trigger(position)

    def close_position(self, exit_price: float) -> Optional[float]:
        if not self.has_open_position():
            return None
        pnl = self._current_position.calculate_pnl(exit_price)
        self._realized_pnl += pnl
        self._balance += pnl
        
        self._logger.info(f"[CLOSE {self._current_position.position_type}] P={exit_price} PNL={pnl:.2f}")
        self.close_position_event.trigger(self._current_position)
        self._current_position = None
        return pnl

    def calculate_equity(self, current_price: float) -> float:
        pnl = self._current_position.calculate_pnl(current_price) if self.has_open_position() else 0.0
        return self._balance + pnl

    def calculate_exposure(self) -> float:
        return self._current_position.calculate_notional() if self.has_open_position() else 0.0

    def get_portfolio_snapshot(self, current_price: float) -> PortfolioSnapshot:
        equity = self.calculate_equity(current_price)
        exposure = self.calculate_exposure()
        return PortfolioSnapshot(
            timestamp=int(datetime.now().timestamp()),
            balance=self._balance,
            equity=equity,
            margin_used=exposure,
            unrealized_pnl=equity - self._balance,
            realized_pnl=self._realized_pnl,
            exposure=exposure,
            open_positions= 1 if self.has_open_position() else 0
        )
