import time
from typing import Optional, List
from models.position import Position
from models.position_type import PositionType
from models.trade_execution import TradeExecution
from state.market_state import MarketState
from engines.risk_engine import RiskEngine
from engines.portfolio_engine import PortfolioEngine
from config.config_manager import ConfigManager


class ExecutionEngine:
    
    def __init__(self, market_state: MarketState, portfolio_engine: PortfolioEngine, risk_engine: RiskEngine, config_manager: ConfigManager):
        self.market_state = market_state
        self.portfolio = portfolio_engine
        self.risk = risk_engine
        self.config_manager = config_manager

        self._execution_history: List[TradeExecution] = []
        self._trades_count = 0

    def execute_market_order(
        self,
        position_type: PositionType,
        market_price: float,
        quantity: float,
        leverage: float,
        stop_loss: float,
        take_profit: float,
        ) -> Optional[TradeExecution]:

        taker_fee = self.config_manager.get_config().execution.taker_fee
        notional = market_price * quantity
        fees = notional * taker_fee


        if self.portfolio.has_open_position() or not self.risk.check_risk_limits(
            balance=self.portfolio.get_balance(),
            equity=self.portfolio.calculate_equity(market_price),
            current_exposure=self.portfolio.calculate_exposure(),
            leverage=leverage
        ):
            return TradeExecution(
                side=position_type, execution_price=0, quantity=0,
                slippage=0, fees=0, latency_ms=0,
                timestamp=int(time.time() * 1000), success=False
            )

        position = Position(
            position_type=position_type,
            entry_price=market_price,
            quantity=quantity,
            leverage=leverage,
            timestamp=int(time.time() * 1000),
            stop_loss=stop_loss or 0,
            take_profit=take_profit or 0,
            total_fees_paid=fees
        )

        self.portfolio.open_position(position)

        trade_execution = TradeExecution(
            side=position_type, execution_price=market_price,
            quantity=quantity, slippage=0, fees=fees,
            latency_ms=0, timestamp=int(time.time() * 1000), success=True
        )
        self._execution_history.append(trade_execution)
        self._trades_count += 1

        return trade_execution

    def close_position(self, current_price: float) -> Optional[float]:
        return self.portfolio.close_position(current_price)
