import numpy as np

class MicrostructureEngine:

    def __init__(self, structure_engine, liquidity_engine, order_flow_engine):

        self.structure_engine = structure_engine
        self.liquidity_engine = liquidity_engine
        self.order_flow_engine = order_flow_engine

    # =====================================================
    # LONG CONTEXT
    # =====================================================

    def long_context(self) -> float:

        structure = float(self.structure_engine.bos_up())
        liquidity = float(self.liquidity_engine.sweep_low())
        flow = float(self.order_flow_engine.calculate_absorption_buy())

        score = (
            0.5 * structure +
            0.3 * liquidity +
            0.2 * flow
        )

        return float(np.clip(score, 0.0, 1.0))

    # =====================================================
    # SHORT CONTEXT
    # =====================================================

    def short_context(self) -> float:

        structure = float(self.structure_engine.bos_down())
        liquidity = float(self.liquidity_engine.sweep_high())
        flow = float(self.order_flow_engine.calculate_absorption_sell())

        score = (
            0.5 * structure +
            0.3 * liquidity +
            0.2 * flow
        )

        return float(np.clip(score, 0.0, 1.0))