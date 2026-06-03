import asyncio


class RetryUtils:

    @staticmethod
    async def retry_async(
        func,
        retries=5,
        delay=1
    ):

        last_exception = None

        for _ in range(retries):

            try:
                return await func()

            except Exception as e:

                last_exception = e

                await asyncio.sleep(delay)

        raise last_exception