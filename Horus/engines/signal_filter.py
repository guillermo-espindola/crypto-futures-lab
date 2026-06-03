class SignalFilter:

    @staticmethod
    def volume_filter(
        candles,
        threshold=1.5
    ):

        volume = candles["volume"]

        avg = (
            volume
            .rolling(20)
            .mean()
        )

        result = volume > (avg * threshold)

        return result.fillna(False)

    @staticmethod
    def spread_filter(
        spread,
        max_spread
    ):

        return spread <= max_spread

    @staticmethod
    def volatility_filter(
        atr,
        minimum
    ):

        return atr >= minimum