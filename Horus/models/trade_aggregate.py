from dataclasses import dataclass

@dataclass(slots=True)
class TradeAggregate:
    start_time: int
    end_time: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    delta: float
    buy_volume: float
    sell_volume: float
    trade_count: int
    buy_count: int
    sell_count: int
    vwap: float
    max_trade_quantity: float
    min_trade_quantity: float
    max_trade_amount: float
    min_trade_amount: float
    max_buy_qty: float
    max_buy_qty_price: float
    max_sell_qty: float
    max_sell_qty_price: float
    max_buy_amount: float
    max_buy_amount_price: float
    max_sell_amount: float
    max_sell_amount_price: float
    # VSA & Intensity Metrics
    tick_range: float
    displacement: float
    avg_trade_size: float
    normalized_delta: float
    buy_volume_pct: float