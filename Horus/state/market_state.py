import pandas as pd
import numpy as np
from typing import List, Optional, Dict

from models.aggregate_trade import AggregateTrade
from models.candle import Candle
from models.candle_snapshot import CandleSnapshot
from models.liquidation import Liquidation
from models.market_snapshot import MarketSnapshot
from models.orderbook import OrderBook
from models.orderbook_snapshot import OrderBookSnapshot
from models.trade import Trade

from state.aggregate_trade_state import AggregateTradeState
from state.candles_state import CandlesState
from state.orderbook_state import OrderBookState
from state.liquidation_state import LiquidationState
from state.trade_state import TradeState

class MarketState:
    def __init__(self, symbol: str,
                 candles_state: CandlesState,
                 orderbook_state: OrderBookState,
                 aggregate_trade_state: AggregateTradeState,
                 liquidation_state: LiquidationState,
                 trades_state: TradeState):
        self.symbol = symbol
        self._candles_state = candles_state
        self._orderbooks = orderbook_state
        self._aggregate_trades = aggregate_trade_state
        self._liquidations = liquidation_state
        self._trades = trades_state

        # Caching layer
        self._df_cache: Dict[str, pd.DataFrame] = {}
        self._last_candle_time: Dict[str, int] = {}
        self._snapshot_cache: Dict[str, CandleSnapshot] = {}

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

    def get_last_candle(self, symbol: str, timeframe: str) -> Optional[Candle]:
        return self._candles_state.last(symbol, timeframe)

    # =====================================================
    # AGGREGATE TRADES
    # =====================================================

    def add_aggregate_trade(self, aggregate_trade: AggregateTrade):
        self._aggregate_trades.add(aggregate_trade)

    def get_aggregate_trades(self, symbol: str) -> List[AggregateTrade]:
        return self._aggregate_trades.get(symbol)

    def last_aggregate_trade(self, symbol: str) -> Optional[AggregateTrade]:
        return self._aggregate_trades.last(symbol)

    # =====================================================
    # TRADES
    # =====================================================

    def add_trade(self, trade: Trade):
        self._trades.add(trade)

    def get_trades(self, symbol: str) -> List[Trade]:
        return self._trades.get(symbol)

    def last_trade(self, symbol: str) -> Optional[Trade]:
        return self._trades.last(symbol)

    # =====================================================
    # ORDERBOOKS
    # =====================================================

    def add_orderbook(self, ob: OrderBook):
        self._orderbooks.update(ob)

    def get_orderbook(self, symbol: str) -> Optional[OrderBookSnapshot]:
        return self._orderbooks.get(symbol)

    def get_sorted_bids(self, symbol: str, limit: int = 20) -> List[Tuple[float, float]]:
        """Returns top N bids from the local book."""
        return self._orderbooks.get_sorted_bids(symbol, limit)

    def get_sorted_asks(self, symbol: str, limit: int = 20) -> List[Tuple[float, float]]:
        """Returns top N asks from the local book."""
        return self._orderbooks.get_sorted_asks(symbol, limit)

    # =====================================================
    # LIQUIDATIONS
    # =====================================================

    def add_liquidation(self, liq: Liquidation):
        self._liquidations.add(liq)

    def get_liquidations(self, symbol: str) -> List[Liquidation]:
        return self._liquidations.get(symbol)

    def last_liquidation(self, symbol: str) -> Optional[Liquidation]:
        return self._liquidations.last(symbol)

    # =====================================================
    # HELPERS
    # =====================================================

    def get_last_price(self, symbol: str, timeframe: str) -> float:
        candle = self.get_last_candle(symbol, timeframe)
        if candle:
            return candle.close
        return 0.0

    def get_snapshot(self, symbol: str, timeframe: str, timestamp: float) -> MarketSnapshot:
        """
        Creates a synchronized snapshot of the market state.
        """
        return MarketSnapshot(
            symbol=symbol,
            candles_df=self.get_candles_df(symbol, timeframe),
            trades=self.get_trades(symbol),
            orderbook=self.get_orderbook(symbol),
            liquidations=self.get_liquidations(symbol),
            timestamp=timestamp
        )
