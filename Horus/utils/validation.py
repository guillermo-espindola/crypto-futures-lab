import math
import pandas as pd


class ValidationUtils:

    # =====================================================
    # VALID NUMBER
    # =====================================================

    @staticmethod
    def valid_number(value):

        if value is None:
            return False

        if (
            math.isnan(value)
            or
            math.isinf(value)
        ):
            return False

        return True

    # =====================================================
    # VALID PRICE
    # =====================================================

    @staticmethod
    def valid_price(value):

        if not ValidationUtils.valid_number(value):
            return False

        return value > 0

    # =====================================================
    # VALID QUANTITY
    # =====================================================

    @staticmethod
    def valid_quantity(value):

        if not ValidationUtils.valid_number(value):
            return False

        return value >= 0

    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    @staticmethod
    def validate_columns(
        df,
        columns
    ):

        missing = [
            c for c in columns
            if c not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

    # =====================================================
    # VALID DATAFRAME
    # =====================================================

    @staticmethod
    def validate_dataframe(df):

        if not isinstance(df, pd.DataFrame):
            raise TypeError(
                "Expected DataFrame"
            )

        if len(df) == 0:
            raise ValueError(
                "Empty DataFrame"
            )