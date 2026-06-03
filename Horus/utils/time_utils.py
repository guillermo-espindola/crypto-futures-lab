import time
from datetime import datetime, timezone


class TimeUtils:

    # =====================================================
    # NOW MS
    # =====================================================

    @staticmethod
    def now_ms():

        return int(
            time.time() * 1000
        )

    # =====================================================
    # TO DATETIME
    # =====================================================

    @staticmethod
    def to_datetime(timestamp_ms):

        return datetime.fromtimestamp(
            timestamp_ms / 1000,
            tz=timezone.utc
        )

    # =====================================================
    # LATENCY
    # =====================================================

    @staticmethod
    def latency_ms(start):

        return (
            TimeUtils.now_ms()
            - start
        )

    # =====================================================
    # ELAPSED
    # =====================================================

    @staticmethod
    def elapsed_seconds(start):

        return (
            time.time() - start
        )