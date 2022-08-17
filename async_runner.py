import asyncio
from typing import Set, Coroutine


__all__ = [
    "loop",
    "AlreadyRunError",
    "run_coro",
]


loop = asyncio.new_event_loop()
running_tasks: Set[int] = set()


class AlreadyRunError(Exception):
    """
    Error to prevent multiple tasks started by one user.
    """
    pass


async def run_coro(user_key: int, coro: Coroutine):
    """
    Function for starting asynchronous tasks.
    Checks if there are tasks already running for this user, and if not,
    sets the execution flag and executes the handler.
    """

    if user_key in running_tasks:
        raise AlreadyRunError("The task has already started")

    running_tasks.add(user_key)
    try:
        await coro
    finally:
        running_tasks.remove(user_key)
