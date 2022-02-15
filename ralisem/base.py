import abc
import datetime


class TimeRateLimitSemaphoreBase(abc.ABC):
    def __init__(self, access_times: int, per: datetime.timedelta):
        self._per_seconds = per.seconds
        self._access_times = access_times

    @abc.abstractmethod
    async def acquire(self) -> None:
        pass

    def release(self) -> None:
        pass

    @abc.abstractmethod
    def is_locked(self) -> bool:
        pass

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()
