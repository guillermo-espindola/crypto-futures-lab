import numpy as np
from collections import deque
from typing import List, Tuple, Optional
from dataclasses import dataclass

from state.market_state import MarketState
from utils.config_manager import ConfigManager
from utils.logger import Logger
from models.trade import Trade
from models.orderbook import OrderBook

@dataclass
class FlowState:
    """Current window metrics for OrderFlow"""
    delta: float = 0.0
    price_change: float = 0.0
    volatility: float = 0.0
    pressure: float = 0.0
    impact: float = 0.0

class OrderFlowEngine:
    """
    Order Flow Engine
    ----------------
    Analyzes trade delta, market impact, and absorption.
    Integrates Order Book depth to calculate real liquidity pressure.
    """

    def __init__(self, market_state: MarketState, symbol: str, logger: Optional[Logger] = None):
        self.market_state = market_state
        self.symbol = symbol
        self.config = ConfigManager()
        self.logger = logger or Logger(OrderFlowEngine)

        # Rolling history of impact values
        self.impact_history = deque(maxlen=2000)
        self._current_state = FlowState()

    # =====================================================
    # CORE METRICS
    # =====================================================

    def _get_liquidity_depth(self) -> float:
        """Returns the sum of volumes in top 5 levels of the orderbook."""
        ob = self.market_state.get_orderbook(self.symbol)
        if not ob:
            return 0.0
        bid_vol = sum([float(b[1]) for b in ob.bids[:5]])
        ask_vol = sum([float(a[1]) for a in ob.asks[:5]])
        return bid_vol + ask_vol

    def _calculate_delta(self, trades: List[Trade]) -> float:
        buys = 0.0
        sells = 0.0
        for trade in trades:
            q = float(trade.quantity)
            if trade.is_buyer_maker: # Aggressive Sell
                sells += q
            else: # Aggressive Buy
                buys += q
        return buys - sells

    def _calculate_impact(self, delta: float, price_change: float, volatility: float, pressure: float) -> float:
        norm_delta = abs(delta) + 1e-9
        # Impact is how much price moves relative to volume and liquidity depth
        # If pressure is high, buyers need more volume to move price UP
        impact = abs(price_change) / (norm_delta * pressure + 1e-9)
        return impact / (volatility + 1e-9)

    # =====================================================
    # PUBLIC API
    # =====================================================

    def update_metrics(self):
        """
        Calculates current tick-level state and updates the impact history.
        """
        trades = self.market_state.get_trades(self.symbol)
        if len(trades) < 50: return

        window = self.config.get("order_flow", "window_size") or 50
        recent = trades[-window:]

        delta = self._calculate_delta(recent)
        price_change = float(recent[-1].price) - float(recent[0].price)

        prices = np.array([float(t.price) for t in recent])
        volatility = np.std(np.diff(prices) / prices[:-1]) + 1e-9

        # New Liquidity Pressure: Delta / Total Depth
        depth = self._get_liquidity_depth()
        pressure = abs(delta) / (depth + 1e-9)

        impact = self._calculate_impact(delta, price_change, volatility, pressure)

        # Update internal state
        self._current_state = FlowState(
            delta=delta,
            price_change=price_change,
            volatility=volatility,
            pressure=pressure,
            impact=impact
        )

        self.impact_history.append(impact)

    def calculate_absorption(self, side: str) -> float:
        """
        Calculates absorption score [0, 1].
        Sells absorbed by buyers (bullish) / Buys absorbed by sellers (bearish).
        """
        state = self._current_state

        # Directional Filter
        if side == "buy" and state.delta <= 0: return 0.0
        if side == "sell" and state.delta >= 0: return 0.0

        impact = state.impact
        if len(self.impact_history) < 100: return 0.0

        avg = np.mean(self.impact_history)
        std = np.std(self.impact_history) + 1e-9

        zscore = (impact - avg) / std
        # Low impact relative to high aggression = absorption
        return float(np.clip((-zscore) / 3.0, 0.0, 1.0))

    def get_absorption_buy(self) -> float:
        return self.calculate_absorption("buy")

    def get_absorption_sell(self) -> float:
        return self.calculate_absorption("sell")
