
from models.trade import Trade
from models.trade_aggregate import TradeAggregate

class TradeAggregator:
    def __init__(self):
        self._last_aggregate: TradeAggregate | None = None
        self.reset()

    def reset(self):
        self._start_timestamp: int = 0
        self._end_timestamp: int = 0
        self._open_price: float = 0.0
        self._high_price: float = 0.0
        self._low_price: float = float('inf')
        self._close_price: float = 0.0
        self._total_quantity: float = 0.0
        self._buy_volume: float = 0.0
        self._sell_volume: float = 0.0
        self._total_trades: int = 0
        self._buy_count: int = 0
        self._sell_count: int = 0
        self._sum_price_vol: float = 0.0
        self._max_qty: float = 0.0
        self._min_qty: float = float('inf')
        self._max_amt: float = 0.0
        self._min_amt: float = float('inf')

        self._max_buy_qty: float = 0.0
        self._max_buy_qty_price: float = 0.0
        self._max_sell_qty: float = 0.0
        self._max_sell_qty_price: float = 0.0
        self._max_buy_amt: float = 0.0
        self._max_buy_amt_price: float = 0.0
        self._max_sell_amt: float = 0.0
        self._max_sell_amt_price: float = 0.0

    def aggregate(self, trade: Trade):
        if self._start_timestamp == 0:
            self._start_timestamp = trade.trade_time
            self._open_price = trade.price

        self._end_timestamp = trade.trade_time
        self._close_price = trade.price
        self._high_price = max(self._high_price, trade.price)
        self._low_price = min(self._low_price, trade.price)

        amount = trade.price * trade.quantity
        self._total_quantity += trade.quantity
        self._total_trades += 1
        self._sum_price_vol += amount
        self._max_qty = max(self._max_qty, trade.quantity)
        self._min_qty = min(self._min_qty, trade.quantity)
        self._max_amt = max(self._max_amt, amount)
        self._min_amt = min(self._min_amt, amount)

        if trade.is_buyer_maker: # Aggressive Sell
            self._sell_volume += trade.quantity
            self._sell_count += 1
            if trade.quantity > self._max_sell_qty:
                self._max_sell_qty = trade.quantity
                self._max_sell_qty_price = trade.price
            if amount > self._max_sell_amt:
                self._max_sell_amt = amount
                self._max_sell_amt_price = trade.price
        else: # Aggressive Buy
            self._buy_volume += trade.quantity
            self._buy_count += 1
            if trade.quantity > self._max_buy_qty:
                self._max_buy_qty = trade.quantity
                self._max_buy_qty_price = trade.price
            if amount > self._max_buy_amt:
                self._max_buy_amt = amount
                self._max_buy_amt_price = trade.price

    def create(self, current_timestamp: int) -> TradeAggregate:
        if self._total_trades > 0:
            delta = self._buy_volume - self._sell_volume
            volume = self._total_quantity

            aggregate = TradeAggregate(
                start_time=self._start_timestamp,
                end_time=self._end_timestamp,
                open_price=self._open_price,
                high_price=self._high_price,
                low_price=self._low_price,
                close_price=self._close_price,
                volume=volume,
                delta=delta,
                buy_volume=self._buy_volume,
                sell_volume=self._sell_volume,
                trade_count=self._total_trades,
                buy_count=self._buy_count,
                sell_count=self._sell_count,
                vwap=self._sum_price_vol / volume if volume > 0 else self._close_price,
                max_trade_quantity=self._max_qty,
                min_trade_quantity=self._min_qty,
                max_trade_amount=self._max_amt,
                min_trade_amount=self._min_amt,
                max_buy_qty=self._max_buy_qty,
                max_buy_qty_price=self._max_buy_qty_price,
                max_sell_qty=self._max_sell_qty,
                max_sell_qty_price=self._max_sell_qty_price,
                max_buy_amount=self._max_buy_amt,
                max_buy_amount_price=self._max_buy_amt_price,
                max_sell_amount=self._max_sell_amt,
                max_sell_amount_price=self._max_sell_amt_price,
                tick_range=self._high_price - self._low_price,
                displacement=self._close_price - self._open_price,
                avg_trade_size=volume / self._total_trades,
                normalized_delta=delta / volume if volume > 0 else 0.0,
                buy_volume_pct=self._buy_volume / volume if volume > 0 else 0.0
            )
        elif self._last_aggregate:
            prev = self._last_aggregate
            aggregate = TradeAggregate(
                start_time=current_timestamp,
                end_time=current_timestamp,
                open_price=prev.close_price,
                high_price=prev.close_price,
                low_price=prev.close_price,
                close_price=prev.close_price,
                volume=0.0,
                delta=0.0,
                buy_volume=0.0,
                sell_volume=0.0,
                trade_count=0,
                buy_count=0,
                sell_count=0,
                vwap=prev.close_price,
                max_trade_quantity=0.0,
                min_trade_quantity=0.0,
                max_trade_amount=0.0,
                min_trade_amount=0.0,
                max_buy_qty=0.0,
                max_buy_qty_price=0.0,
                max_sell_qty=0.0,
                max_sell_qty_price=0.0,
                max_buy_amount=0.0,
                max_buy_amount_price=0.0,
                max_sell_amount=0.0,
                max_sell_amount_price=0.0,
                tick_range=0.0,
                displacement=0.0,
                avg_trade_size=0.0,
                normalized_delta=0.0,
                buy_volume_pct=0.5 # Neutral
            )
        else:
            aggregate = TradeAggregate(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5)

        self._last_aggregate = aggregate
        self.reset()
        return aggregate
