import asyncio
import random
import time
from typing import Optional, List
from models.position import Position
from models.position_type import PositionType
from models.trade_execution import TradeExecution
from state.market_state import MarketState
from engines.risk_engine import RiskEngine
from engines.portfolio_engine import PortfolioEngine
from utils.config_manager import ConfigManager
from utils.logger import Logger

class ExecutionEngine:
    """
    Execution Engine
    ----------------
    Handles simulated market execution with latency and slippage.
    Implements a feedback loop to track fill quality and slippage.
    """

    def __init__(self, market_state: MarketState, portfolio_engine: PortfolioEngine, risk_engine: RiskEngine):
        self.market_state = market_state
        self.portfolio = portfolio_engine
        self.risk = risk_engine
        self.config = ConfigManager()

        self._execution_history: List[TradeExecution] = []
        self._slippage_accumulator = 0.0
        self._trades_count = 0

    def _calculate_average_slippage(self) -> float:
        if self._trades_count == 0: return 0.0
        return self._slippage_accumulator / self._trades_count

    def _get_fill_quality(self) -> float:
        """
        Calculates fill quality: 1.0 (perfect) -> 0.0 (terrible).
        Based on actual slippage vs expected slippage factor.
        """
        expected = self.config.get("execution", "slippage_factor") or 0.0005
        if self._trades_count == 0: return 1.0

        avg_slip = self._calculate_average_slippage()
        # Lower is better
        return float(np.clip(expected / (avg_slip + 1e-9), 0.0, 1.0))

    async def execute_market_order(
        self,
        symbol: str,
        position_type: PositionType,
        quantity: float,
        leverage: float = 1.0,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        market_price: float = 0.0
        ) -> Optional[TradeExecution]:

        orderbook = self.market_state.get_orderbook(symbol)
        if orderbook is None: return None

        # 1. Price Selection
        if position_type == PositionType.LONG:
            best_ask = orderbook.best_ask()
            if best_ask is None: return None
            base_price = best_ask[0]
        else:
            best_bid = orderbook.best_bid()
            if best_bid is None: return None
            base_price = best_bid[0]

        # 2. Latency Simulation
        base_latency = self.config.get("execution", "latency_ms") or 50
        latency = int(base_latency * random.uniform(0.5, 2.0))
        await asyncio.sleep(latency / 1000)

        # 3. Slippage Model
        slip_factor = self.config.get("execution", "slippage_factor") or 0.0005
        slippage = base_price * slip_factor * random.uniform(0.5, 2.0)
        execution_price = (base_price + slippage) if position_type == PositionType.LONG else (base_price - slippage)

        # 4. Fees
        taker_fee = self.config.get("execution", "taker_fee") or 0.0004
        notional = execution_price * quantity
        fees = notional * taker_fee

        # 5. Risk Approval
        equity = self.portfolio.calculate_equity(execution_price)
        current_exposure = self.portfolio.calculate_exposure()

        if self.portfolio.has_open_position() or not self.risk.check_risk_limits(
            balance=self.portfolio.get_balance(),
            equity=equity,
            current_exposure=current_exposure,
            leverage=leverage
        ):
            return TradeExecution(
                symbol=symbol, side=position_type, execution_price=0, quantity=0,
                slippage=0, fees=0, latency_ms=latency,
                timestamp=int(time.time() * 1000), success=False
            )

        # 6. Position Creation
        position = Position(
            symbol=symbol,
            position_type=position_type,
            market_price=market_price,
            entry_price=execution_price,
            quantity=quantity,
            leverage=leverage,
            timestamp=int(time.time() * 1000),
            stop_loss=stop_loss or 0,
            take_profit=take_profit or 0,
            total_fees_paid=fees
        )

        self.portfolio.open_position(position)

        # Update Feedback Loop
        exec_result = TradeExecution(
            symbol=symbol, side=position_type, execution_price=execution_price,
            quantity=quantity, slippage=slippage, fees=fees,
            latency_ms=latency, timestamp=int(time.time() * 1000), success=True
        )
        self._execution_history.append(exec_result)
        self._slippage_accumulator += abs(slippage / base_price)
        self._trades_count += 1

        return exec_result

    async def close_position(self, current_price: float) -> Optional[float]:
        return self.portfolio.close_position(current_price)
