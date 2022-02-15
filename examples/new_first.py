import asyncio
import datetime
import time

from ralisem import FixedNewFirstDelaySemaphore, TimeRateLimitSemaphoreBase


async def task(task_no: int, sem: TimeRateLimitSemaphoreBase):
    async with sem:
        print(f"Task {task_no} continued at {time.monotonic():.3}s")


async def main():
    sem = FixedNewFirstDelaySemaphore(
        access_times=3, per=datetime.timedelta(seconds=1)
    )
    tasks = [
        task(i, sem)
        for i in range(1000)
    ]
    await asyncio.gather(*tasks)


asyncio.run(main())
