import numpy as np
import pandas as pd


class FeatureNormalizer:

    @staticmethod
    def minmax(series):

        min_val = series.min()
        max_val = series.max()

        if max_val - min_val == 0:
            return pd.Series(
                0,
                index=series.index
            )

        return (
            (series - min_val)
            /
            (max_val - min_val)
        )

    @staticmethod
    def zscore(series):

        mean = series.mean()
        std = series.std()

        if std == 0:
            return pd.Series(
                0,
                index=series.index
            )

        return (
            (series - mean)
            / std
        )