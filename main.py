__version__ = "1.3.5"

import asyncio
from typing import List, Coroutine

from envs import envs
from bot import user_bot_init, admin_bot_init, test_bot_init


async def start_bots(start_funcs: List[Coroutine]):
    await asyncio.gather(*start_funcs)
    while True:
        await asyncio.sleep(1)


if envs.get("DEBUG", False):
    # test bot for development
    TOKEN_TEST = envs["TOKEN_TEST"]
    bot_list = [
        test_bot_init(TOKEN_TEST),
    ]
else:
    TOKEN_USER = envs["TOKEN_USER"]
    TOKEN_ADMIN = envs["TOKEN_ADMIN"]
    bot_list = [
        user_bot_init(TOKEN_USER),
        admin_bot_init(TOKEN_ADMIN),
    ]


asyncio.run(start_bots(bot_list))
