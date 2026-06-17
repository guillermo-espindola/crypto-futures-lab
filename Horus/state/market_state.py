import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple

from models.aggregate_trade import AggregateTrade
from models.candle import Candle
from models.candle_snapshot import CandleSnapshot
from models.liquidation import Liquidation
from models.market_snapshot import MarketSnapshot
from models.orderbook_depth_update import OrderBookDepthUpdate
from models.orderbook import OrderBook
from models.trade import Trade

from state.aggregate_trade_state import AggregateTradeState
from state.candles_state import CandlesState
from state.orderbook_state import OrderBookState
from state.liquidation_state import LiquidationState
from state.trade_state import TradeState

from utils.aggregate_trade_candle_builder import AggregateTradeCandleBuilder

class MarketState:
    def __init__(self, symbol: str,
                 candles_state: CandlesState,
                 orderbook_state: OrderBookState,
                 aggregate_trade_state: AggregateTradeState,
                 liquidation_state: LiquidationState,
                 trades_state: TradeState,
                 aggregate_trade_candle_builder: AggregateTradeCandleBuilder):
        self._symbol = symbol
        self._candles_state = candles_state
        self._orderbook_state = orderbook_state
        self._aggregate_trade_state = aggregate_trade_state
        self._liquidation_state = liquidation_state
        self._trade_state = trades_state
        self._aggregate_trade_candle_builder = aggregate_trade_candle_builder

        self._current_price: float = 0.0

        # Caching layer
        self._df_cache: Dict[str, pd.DataFrame] = {}
        self._last_candle_time: Dict[str, int] = {}
        self._snapshot_cache: Dict[str, CandleSnapshot] = {}

    # CURRENT PRICE

    def set_current_price(self, current_price: float):
        self._current_price = current_price
    
    def get_current_price(self) -> float:
        return self._current_price

    # =====================================================
    # CANDLES
    # =====================================================

    def add_candle(self, candle: Candle):
        self._candles_state.add(candle)
        # Invalidate cache if candle time changed
        if candle.open_time != self._last_candle_time.get(candle.timeframe, 0):
            self._df_cache.pop(candle.timeframe, None)
            self._snapshot_cache.pop(candle.timeframe, None)
            self._last_candle_time[candle.timeframe] = candle.open_time

    def get_candles(self, symbol: str, timeframe: str) -> List[Candle]:
        return self._candles_state.get(symbol, timeframe)

    def get_candles_df(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Returns a cached DataFrame of candles.
        Only rebuilds if the latest candle has changed.
        """
        if timeframe in self._df_cache:
            return self._df_cache[timeframe]

        candles = self.get_candles(symbol, timeframe)
        if not candles:
            return pd.DataFrame()

        df = pd.DataFrame([c.to_dict() for c in candles])
        # Standardize numeric columns
        numeric_cols = ["open", "high", "low", "close", "volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=numeric_cols).reset_index(drop=True)
        self._df_cache[timeframe] = df
        return df

    def get_candle_snapshot(self, symbol: str, timeframe: str) -> Optional[CandleSnapshot]:
        """
        Returns a cached snapshot of the current candle and its key metrics (like ATR).
        Recalculates only when a new candle arrives.
        """
        if timeframe in self._snapshot_cache:
            return self._snapshot_cache[timeframe]

        df = self.get_candles_df(symbol, timeframe)
        if df.empty:
            return None

        last_candle = df.iloc[-1]

        # Calculate ATR (14 period) using EWM for better reactivity
        high_low = df['high'] - df['low']
        high_cp = np.abs(df['high'] - df['close'].shift(1))
        low_cp = np.abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        atr = tr.ewm(span=14, adjust=False).mean().iloc[-1] if len(tr) >= 14 else df['high'].iloc[-1] - df['low'].iloc[-1]

        snapshot = CandleSnapshot(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=int(last_candle['open_time']),
            open=float(last_candle['open']),
            high=float(last_candle['high']),
            low=float(last_candle['low']),
            close=float(last_candle['close']),
            volume=float(last_candle['volume']),
            atr=float(atr),
            is_closed=True # Adjusted by the loop if needed
        )

        self._snapshot_cache[timeframe] = snapshot
        return snapshot
    
    # =====================================================
    # AGGREGATE TRADES
    # =====================================================

    def add_aggregate_trade(self, aggregate_trade: AggregateTrade):
        self._aggregate_trade_state.add(aggregate_trade)
        self._aggregate_trade_candle_builder.add(aggregate_trade)

    def get_aggregate_trades(self, symbol: str) -> List[AggregateTrade]:
        return self._aggregate_trade_state.get(symbol)

    def last_aggregate_trade(self, symbol: str) -> Optional[AggregateTrade]:
        return self._aggregate_trade_state.last(symbol)

    # =====================================================
    # TRADES
    # =====================================================

    def add_trade(self, trade: Trade):
        self._trade_state.add(trade)

    def get_current_trades(self) -> List[Trade]:
        return self._trade_state.get_current_trades()

    # =====================================================
    # ORDERBOOK
    # =====================================================

    def update_orderbook(self, orderbook_depth_update: OrderBookDepthUpdate):
        self._orderbook_state.update(orderbook_depth_update)

    def get_orderbook(self) -> Optional[OrderBook]:
        return self._orderbook_state.get_orderbook()

    def get_sorted_bids(self, limit: int = 20) -> List[Tuple[float, float]]:
        """Returns top N bids from the local book."""
        return self._orderbook_state.get_sorted_bids(limit)

    def get_sorted_asks(self, limit: int = 20) -> List[Tuple[float, float]]:
        """Returns top N asks from the local book."""
        return self._orderbook_state.get_sorted_asks(limit)

    # =====================================================
    # LIQUIDATIONS
    # =====================================================

    def add_liquidation(self, liq: Liquidation):
        self._liquidation_state.add(liq)

    def get_liquidations(self, symbol: str) -> List[Liquidation]:
        return self._liquidation_state.get(symbol)

    def last_liquidation(self, symbol: str) -> Optional[Liquidation]:
        return self._liquidation_state.last(symbol)

    # =====================================================
    # HELPERS
    # =====================================================

    def get_snapshot(self, symbol: str, timeframe: str, timestamp: float) -> MarketSnapshot:
        """
        Creates a synchronized snapshot of the market state.
        """
        return MarketSnapshot(
            symbol=symbol,
            candles_df=self.get_candles_df(symbol, timeframe),
            trades=self.get_current_trades(symbol),
            orderbook=self.get_orderbook(),
            liquidations=self.get_liquidations(symbol),
            timestamp=timestamp
        )
