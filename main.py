__version__ = "0.95"

from envs import envs
from bot import bot_main


if envs.get("DEBUG", False):
    # test bot for development
    TOKEN = envs["TOKEN_TEST"]
else:
    TOKEN = envs["TOKEN"]


bot_main(TOKEN)
