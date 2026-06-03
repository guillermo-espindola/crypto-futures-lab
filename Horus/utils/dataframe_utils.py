import pandas as pd
import numpy as np


class DataFrameUtils:

    # =====================================================
    # OPTIMIZE
    # =====================================================

    @staticmethod
    def optimize(df):

        for col in df.columns:

            if df[col].dtype == "float64":
                df[col] = df[col].astype(
                    np.float32
                )

            elif df[col].dtype == "int64":
                df[col] = df[col].astype(
                    np.int32
                )

        return df

    # =====================================================
    # SORT
    # =====================================================

    @staticmethod
    def sort_by_time(
        df,
        column="open_time"
    ):

        return (
            df
            .sort_values(column)
            .reset_index(drop=True)
        )

    # =====================================================
    # DEDUP
    # =====================================================

    @staticmethod
    def deduplicate(
        df,
        subset
    ):

        return (
            df
            .drop_duplicates(
                subset=subset
            )
            .reset_index(drop=True)
        )