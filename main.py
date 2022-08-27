__version__ = "1.0.0"

from envs import envs
from bot import bot_init


if envs.get("DEBUG", False):
    # test bot for development
    TOKEN = envs["TOKEN_TEST"]
else:
    TOKEN = envs["TOKEN"]

bot_init(TOKEN)
