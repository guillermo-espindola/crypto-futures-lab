import asyncio
from datetime import datetime
from typing import Optional

from models.candle import Candle
from notification.notifier_interface import INotifier

from state.market_state import MarketState
from infrastructure.kafka_consumer import KafkaConsumer

from engines.structure_engine import StructureEngine
from engines.liquidity_engine import LiquidityEngine
from engines.order_flow_engine import OrderFlowEngine
from engines.regime_engine import RegimeEngine
from engines.order_book_engine import OrderBookEngine
from engines.scoring_engine import ScoringEngine
from engines.portfolio_engine import PortfolioEngine
from engines.risk_engine import RiskEngine
from engines.execution_engine import ExecutionEngine
from utils.config_manager import ConfigManager
from utils.logger_interface import ILogger

class TradingLoop:
    def __init__(self,
                 symbol: str,
                 market_state: MarketState,
                 kafka_consumer: KafkaConsumer,
                 structure_engine: StructureEngine,
                 liquidity_engine: LiquidityEngine,
                 order_flow_engine: OrderFlowEngine,
                 regime_engine: RegimeEngine,
                 order_book_engine: OrderBookEngine,
                 scoring_engine: ScoringEngine,
                 portfolio_engine: PortfolioEngine,
                 risk_engine: RiskEngine,
                 execution_engine: ExecutionEngine,
                 notifier: INotifier,
                 logger: ILogger):

        self._symbol = symbol
        self._market_state = market_state
        self._kafka_consumer = kafka_consumer
        self._structure_engine = structure_engine
        self._liquidity_engine = liquidity_engine
        self._order_flow_engine = order_flow_engine
        self._regime_engine = regime_engine
        self._order_book_engine = order_book_engine
        self._scoring_engine = scoring_engine
        self._portfolio_engine = portfolio_engine
        self._risk_engine = risk_engine
        self._execution_engine = execution_engine
        self._notifier = notifier
        self._logger = logger
        self.config = ConfigManager()

        # Signal Smoothing (EMA)
        self.last_resistance: Optional[float] = None
        self.last_support: Optional[float] = None
        self.long_score_ema = 0.0
        self.short_score_ema = 0.0

        # Confirmations
        self.long_confirmations = 0
        self.short_confirmations = 0

        # Cooldown
        self.last_trade_timestamp = 0.0

    def _update_ema(self, long_score: float, short_score: float):
        a = self.config.get("scoring", "ema_alpha") or 0.25
        self.long_score_ema = a * long_score + (1 - a) * self.long_score_ema
        self.short_score_ema = a * short_score + (1 - a) * self.short_score_ema

    def _update_confirmations(self):
        threshold = self.config.get("scoring", "confirmation_threshold") or 2

        if self.long_score_ema > 0.5: # Calibrated midpoint
            self.long_confirmations += 1
        else:
            self.long_confirmations = 0

        if self.short_score_ema > 0.5:
            self.short_confirmations += 1
        else:
            self.short_confirmations = 0

    def _cooldown_active(self) -> bool:
        now = datetime.now().timestamp()
        cooldown = self.config.get("behavior", "cooldown_seconds") or 10
        return (now - self.last_trade_timestamp) < cooldown

    def _generate_signal(self) -> Optional[str]:
        if self._cooldown_active():
            return None

        threshold = self.config.get("scoring", "confirmation_threshold") or 2
        if self.long_confirmations >= threshold and self.long_score_ema > self.short_score_ema:
            return "LONG"

        if self.short_confirmations >= threshold and self.short_score_ema > self.long_score_ema:
            return "SHORT"

        return None

    def on_new_candle(self, candle: Candle):
        # Structure key levels update
        resistance, support = self._structure_engine.get_key_levels()
        self._logger.info(f"CANDLE UPDATE: Resistance={resistance}, Support={support}")
        self.last_resistance = resistance if resistance is not None else self.last_resistance
        self.last_support = support if support is not None else self.last_support

    async def run(self, sleep_time: float):
        self._logger.info(f"[{datetime.now()}] Trading loop started for {self._symbol}")
        try:
            while True:
                # 1. UPDATE MARKET DATA
                await self._kafka_consumer.poll_events()
                current_price = self._market_state.get_last_price(self._symbol, "1m")

                # 2. HIERARCHICAL PIPELINE

                # A. Order Flow Update (Tick-based)
                self._order_flow_engine.update_metrics()

                # B. Scoring Fusion (Fuses tick-flow with cached candle snapshots)
                long_score, short_score = self._scoring_engine.compute_scores()
                regime_val = self._regime_engine.regime_score()
                eff_val = self._regime_engine.market_efficiency()

                # C. Smoothing & Confirmations
                self._update_ema(long_score, short_score)
                self._update_confirmations()

                # 3. POSITION MANAGEMENT
                if current_price > 0:
                    for pos in list(self._portfolio_engine._positions):
                        close_reason = None
                        if pos.side == "LONG" and current_price <= pos.stop_loss:
                            close_reason = "STOP LOSS"
                        elif pos.side == "SHORT" and current_price >= pos.stop_loss:
                            close_reason = "STOP LOSS"
                        elif pos.side == "LONG" and current_price >= pos.take_profit:
                            close_reason = "TAKE PROFIT"
                        elif pos.side == "SHORT" and current_price <= pos.take_profit:
                            close_reason = "TAKE PROFIT"
                        elif pos.side == "LONG" and self.short_confirmations >= 3 and self.short_score_ema > 0.7:
                            close_reason = "REVERSE SIGNAL"
                        elif pos.side == "SHORT" and self.long_confirmations >= 3 and self.long_score_ema > 0.7:
                            close_reason = "REVERSE SIGNAL"

                        if close_reason:
                            pnl = await self._execution_engine.close_position(pos)
                            if pnl is not None:
                                msg = f"CLOSED {pos.side} Q={pos.quantity:.4f} P={current_price:.6f} REASON={close_reason} PnL={pnl:.2f}"
                                self._logger.info(msg)
                                self._notifier.notify(msg)

                # 4. ENTRY SIGNAL
                signal = self._generate_signal()

                if signal and not self._portfolio_engine._positions:
                    # Dynamic Stop/Profit
                    tp_pct = 0.02 # Simplified, should be in config
                    sl_pct = 0.01

                    stop_loss = current_price * (1 - sl_pct) if signal == "LONG" else current_price * (1 + sl_pct)
                    take_profit = current_price * (1 + tp_pct) if signal == "LONG" else current_price * (1 - tp_pct)

                    # Dynamic Sizing based on Regime
                    qty = self._risk_engine.calculate_position_size(
                        balance=self._portfolio_engine._balance,
                        entry_price=current_price,
                        stop_loss_price=stop_loss,
                        regime_score=regime_val,
                        efficiency_score=eff_val
                    )

                    if qty > 0:
                        result = await self._execution_engine.execute_market_order(
                            symbol=self._symbol,
                            side=signal,
                            quantity=qty,
                            leverage=self.config.get("risk", "max_leverage") or 5,
                            stop_loss=stop_loss,
                            take_profit=take_profit
                        )

                        if result and result.success:
                            self.last_trade_timestamp = datetime.now().timestamp()

                            # FEEDBACK LOOP: Send relative slippage back to RegimeEngine
                            rel_slip = abs(result.slippage / result.execution_price) if result.execution_price > 0 else 0
                            self._regime_engine.apply_execution_feedback(rel_slip)

                            msg = (
                                f"EXECUTED {signal} Q={qty:.4f} P={result.execution_price:.6f} "
                                f"SL={stop_loss:.6f} ({sl_pct:.1%}) TP={take_profit:.6f} ({tp_pct:.1%}) "
                                f"Slippage={result.slippage:.6f}"
                            )
                            self._logger.info(msg)
                            self._notifier.notify(msg)

                # 5. SNAPSHOT LOG
                snapshot = self._portfolio_engine.snapshot({self._symbol: current_price}, int(datetime.now().timestamp()))
                self._logger.info(f"[LEVELS] Resistance={self.last_resistance}, Support={self.last_support}")
                self._logger.info(f"[MARKET] Price={current_price:.6f}, Regime={regime_val:.2f}, Eff={eff_val:.2f}")
                self._logger.info(f"[SCORES] L={long_score:.2f} S={short_score:.2f}, EMA_L={self.long_score_ema:.2f}, EMA_S={self.short_score_ema:.2f}")
                self._logger.info(f"[PORTFOLIO] Equity={snapshot.equity:.2f}, Balance={snapshot.balance:.2f}")

                await asyncio.sleep(sleep_time)

        except Exception as e:
            self._logger.error(f"Loop Error: {e}")
            self._notifier.notify(f"ERROR: {e}")
        finally:
            await self._kafka_consumer.stop()
