class MultiTimeframeBias:

    def __init__(
        self,
        htf_structure,
        ltf_structure
    ):

        self.htf = htf_structure
        self.ltf = ltf_structure

    def bullish(self):

        htf_trend = (
            self.htf
            .trend()
            .iloc[-1]
        )

        ltf_bos = (
            self.ltf
            .bos_up()
            .iloc[-1]
        )

        return (
            htf_trend == "BULL"
            and
            ltf_bos
        )

    def bearish(self):

        htf_trend = (
            self.htf
            .trend()
            .iloc[-1]
        )

        ltf_bos = (
            self.ltf
            .bos_down()
            .iloc[-1]
        )

        return (
            htf_trend == "BEAR"
            and
            ltf_bos
        )