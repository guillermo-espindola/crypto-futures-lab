import math
import numpy as np


class MathUtils:

    # =====================================================
    # SAFE DIVISION
    # =====================================================

    @staticmethod
    def safe_divide(
        numerator,
        denominator,
        default=0.0
    ):

        if denominator == 0:
            return default

        result = numerator / denominator

        if (
            math.isnan(result)
            or
            math.isinf(result)
        ):
            return default

        return result

    # =====================================================
    # CLAMP
    # =====================================================

    @staticmethod
    def clamp(
        value,
        minimum,
        maximum
    ):

        return max(
            minimum,
            min(value, maximum)
        )

    # =====================================================
    # NORMALIZE
    # =====================================================

    @staticmethod
    def normalize(
        value,
        min_value,
        max_value
    ):

        denominator = (
            max_value - min_value
        )

        if denominator == 0:
            return 0.0

        return (
            value - min_value
        ) / denominator

    # =====================================================
    # ROUND SAFE
    # =====================================================

    @staticmethod
    def round_safe(
        value,
        decimals=8
    ):

        if (
            math.isnan(value)
            or
            math.isinf(value)
        ):
            return 0.0

        return round(value, decimals)