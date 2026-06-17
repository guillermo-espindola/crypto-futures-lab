import numpy as np
from collections import deque
from typing import List
from dataclasses import dataclass

from state.market_state import MarketState
from utils.logger_interface import ILogger
from models.trade import Trade

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

    def __init__(self, market_state: MarketState, window_size: int, logger: ILogger):
        self._market_state = market_state
        self._window_size = window_size
        self._logger = logger

        # Rolling history of impact values
        self._impact_history = deque(maxlen=2000)
        self._current_state = FlowState()

    # =====================================================
    # CORE METRICS
    # =====================================================

    def _get_liquidity_depth(self, limit: int) -> float:
        """Returns the sum of volumes in top 5 levels of the orderbook."""
        order_book = self._market_state.get_orderbook()
        if not order_book:
            return 0.0
        
        sorted_bids = self._market_state.get_sorted_bids(limit)
        sorted_asks = self._market_state.get_sorted_asks(limit)

        bid_vol = sum([bid[1] for bid in sorted_bids])
        ask_vol = sum([ask[1] for ask in sorted_asks])

        return bid_vol + ask_vol

    def _calculate_delta(self, trades: List[Trade]) -> float:
        buys = 0.0
        sells = 0.0
        for trade in trades:
            if trade.is_buyer_maker: # Aggressive Sell
                sells += trade.quantity
            else: # Aggressive Buy
                buys += trade.quantity
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
        current_trades = self._market_state.get_current_trades()
        if len(current_trades) < self._window_size: return

        recent_trades = current_trades[-(self._window_size):]

        delta = self._calculate_delta(recent_trades)
        price_change = recent_trades[-1].price - recent_trades[0].price

        np_prices = np.array([recent_trade.price for recent_trade in recent_trades])
        volatility = np.std(np.diff(np_prices) / np_prices[:-1]) + 1e-9

        # New Liquidity Pressure: Delta / Total Depth
        depth = self._get_liquidity_depth(5)
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

        self._impact_history.append(impact)

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
        if len(self._impact_history) < 100: return 0.0

        avg = np.mean(self._impact_history)
        std = np.std(self._impact_history) + 1e-9

        zscore = (impact - avg) / std
        # Low impact relative to high aggression = absorption
        return float(np.clip((-zscore) / 3.0, 0.0, 1.0))

    def get_absorption_buy(self) -> float:
        return self.calculate_absorption("buy")

    def get_absorption_sell(self) -> float:
        return self.calculate_absorption("sell")
