import numpy as np
from typing import Tuple, Dict, List
from state.market_state import MarketState
from utils.config_manager import ConfigManager

class OrderBookEngine:
    """
    Order Book Engine
    -----------------
    Calculates high-frequency order book metrics.
    Integrates depth analysis to identify imbalance, pressure, and liquidity walls.
    """

    def __init__(self, market_state: MarketState, symbol: str, config_manager: ConfigManager):
        self.market_state = market_state
        self.symbol = symbol
        self.config = config_manager

    # =====================================================
    # CORE METRICS
    # =====================================================

    def get_spread(self) -> float:
        """
        Calculates the current bid-ask spread.
        """
        bids = self.market_state.get_sorted_bids(self.symbol, 1)
        asks = self.market_state.get_sorted_asks(self.symbol, 1)

        if not bids or not asks:
            return 0.0

        best_bid = bids[0][0]
        best_ask = asks[0][0]
        return float(best_ask - best_bid)

    def calculate_imbalance(self, depth: int = 10) -> float:
        """
        Calculates the real imbalance between bids and asks.
        Symmetry: (BidVol - AskVol) / (BidVol + AskVol)
        Range: [-1.0, 1.0]
        """
        bids = self.market_state.get_sorted_bids(self.symbol, depth)
        asks = self.market_state.get_sorted_asks(self.symbol, depth)

        if not bids or not asks:
            return 0.0

        bid_vol = sum(qty for _, qty in bids)
        ask_vol = sum(qty for _, qty in asks)

        imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol + 1e-9)
        return float(np.clip(imbalance, -1.0, 1.0))

    def calculate_weighted_imbalance(self, depth: int = 10) -> float:
        """
        Calculates weighted imbalance where closer levels have more weight.
        """
        bids = self.market_state.get_sorted_bids(self.symbol, depth)
        asks = self.market_state.get_sorted_asks(self.symbol, depth)

        if not bids or not asks:
            return 0.0

        # Weights decrease as we go deeper into the book
        weights = np.linspace(1.0, 0.1, depth)

        w_bid_vol = sum(qty * weights[i] for i, (_, qty) in enumerate(bids))
        w_ask_vol = sum(qty * weights[i] for i, (_, qty) in enumerate(asks))

        imbalance = (w_bid_vol - w_ask_vol) / (w_bid_vol + w_ask_vol + 1e-9)
        return float(np.clip(imbalance, -1.0, 1.0))

    def calculate_microprice(self) -> float:
        """
        Calculates the microprice, a leading indicator of the next mid-price move.
        Microprice = (BestBid * AskVol + BestAsk * BidVol) / (BidVol + AskVol)
        """
        bids = self.market_state.get_sorted_bids(self.symbol, 1)
        asks = self.market_state.get_sorted_asks(self.symbol, 1)

        if not bids or not asks:
            return 0.0

        bid_p, bid_v = bids[0]
        ask_p, ask_v = asks[0]

        microprice = (bid_p * ask_v + ask_p * bid_v) / (bid_v + ask_v + 1e-9)
        return float(microprice)

    def detect_liquidity_walls(self, depth: int = 50, threshold_multiplier: float = 3.0) -> Dict[str, List[Tuple[float, float]]]:
        """
        Identifies price levels with volume significantly higher than the average depth.
        Returns a dict with "bids" and "asks" walls.
        """
        bids = self.market_state.get_sorted_bids(self.symbol, depth)
        asks = self.market_state.get_sorted_asks(self.symbol, depth)

        if not bids or not asks:
            return {"bids": [], "asks": []}

        avg_bid_vol = np.mean([qty for _, qty in bids])
        avg_ask_vol = np.mean([qty for _, qty in asks])

        walls_bid = [item for item in bids if item[1] >= avg_bid_vol * threshold_multiplier]
        walls_ask = [item for item in asks if item[1] >= avg_ask_vol * threshold_multiplier]

        return {
            "bids": walls_bid,
            "asks": walls_ask
        }

    def get_pressure(self, depth: int = 10) -> float:
        """
        Calculates general book pressure.
        Positive = Bullish, Negative = Bearish.
        """
        return self.calculate_imbalance(depth)
