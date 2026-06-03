class LiquidationEngine:

    def __init__(self, state):
        self.state = state

    def long_liquidations(self):

        return sum(
            l.quantity
            for l in self.state.liquidations
            if l.side == "SELL"
        )

    def short_liquidations(self):

        return sum(
            l.quantity
            for l in self.state.liquidations
            if l.side == "BUY"
        )

    def long_squeeze(self):

        return (
            self.long_liquidations() >
            self.short_liquidations()
        )

    def short_squeeze(self):

        return (
            self.short_liquidations() >
            self.long_liquidations()
        )