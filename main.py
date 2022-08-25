__version__ = "0.97"

from envs import envs
from bot import bot_main
# from async_runner import loop


if envs.get("DEBUG", False):
    # test bot for development
    TOKEN = envs["TOKEN_TEST"]
else:
    TOKEN = envs["TOKEN"]

# Initializing the bot and starting the run cycle
# loop.run_until_complete(loop.run_in_executor(None, bot_main, TOKEN))
bot_main(TOKEN)
