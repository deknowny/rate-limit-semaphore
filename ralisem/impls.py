import collections
import datetime
import time

import anyio

from ralisem.base import TimeRateLimitSemaphoreBase


class FixedNewPreviousDelaySemaphore(TimeRateLimitSemaphoreBase):
    def __init__(self, access_times: int, per: datetime.timedelta):
        TimeRateLimitSemaphoreBase.__init__(self, access_times, per)
        self.__last_call = 0.0
        self.__required_pause = self._per_seconds / self._access_times

    async def acquire(self) -> None:
        now = time.time()
        time_diff = now - self.__last_call
        if time_diff < self.__required_pause:
            time_to_sleep = self.__required_pause - time_diff
            self.__last_call = now + time_to_sleep
            await anyio.sleep(time_to_sleep)
        else:
            self.__last_call = now

    def is_locked(self) -> bool:
        now = time.time()
        time_diff = now - self.__last_call
        return time_diff < self.__required_pause


class FixedNewFirstDelaySemaphore(TimeRateLimitSemaphoreBase):
    def __init__(self, access_times: int, per: datetime.timedelta):
        TimeRateLimitSemaphoreBase.__init__(self, access_times, per)
        # Used as FIFO
        self.__calls_history: collections.deque[float] = collections.deque(
            maxlen=self._access_times
        )

    async def acquire(self) -> None:
        now = time.time()
        if self.is_locked():
            time_to_sleep = (
                self._per_seconds - now + self.__calls_history.popleft()
            )
            self.__calls_history.append(now + time_to_sleep)
            await anyio.sleep(time_to_sleep)
        else:
            self.__calls_history.append(now)

    def is_locked(self) -> bool:
        now = time.time()
        return (
            len(self.__calls_history) == self._access_times
            and now - self.__calls_history[0] < self._per_seconds
        )
