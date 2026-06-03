from config.orderbook_settings import BULLISH_IMBALANCE_THRESHOLD, BEARISH_IMBALANCE_THRESHOLD

class OrderBookEngine:

    def __init__(self, state):
        self.state = state

    def imbalance(self):

        ob = self.state.last_orderbook()

        if ob is None:
            return 0.5

        bid_volume = sum(q for _, q in ob.bids)
        ask_volume = sum(q for _, q in ob.asks)

        total = bid_volume + ask_volume

        if total == 0:
            return 0.5

        return bid_volume / total

    def spread(self):

        ob = self.state.last_orderbook()

        if ob is None:
            return 0.0

        best_bid = max(p for p, _ in ob.bids)
        best_ask = min(p for p, _ in ob.asks)

        return best_ask - best_bid

    def bullish(self):
        return self.imbalance() > BULLISH_IMBALANCE_THRESHOLD

    def bearish(self):
        return self.imbalance() < BEARISH_IMBALANCE_THRESHOLD