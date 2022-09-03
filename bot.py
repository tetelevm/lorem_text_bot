from typing import Callable, Coroutine

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import BaseFilter, ChatType, TEXT

from logger import logger
from handlers import (
    HandlersType,
    Handler,
    received_message,
    command_start_user,
    command_help_user,
    command_generate,
    command_chinese,
    command_start_admin,
    command_help_admin,
    command_generate_wat,
    command_generate_absurd,
    command_lorem,
    command_translate,
)


__all__ = [
    "user_bot_init",
    "admin_bot_init",
    "test_bot_init",
]


class NoChangeFilter(BaseFilter):
    """
    Filter for new messages only, edited messages are ignored.
    """
    def __call__(self, update: Update) -> bool:
        return bool(update.message)

no_change_filter = NoChangeFilter()


standard_filter = no_change_filter & TEXT


def add_command(
        bot: Application,
        handler_decorator: Callable[[HandlersType], Coroutine],
        command: str,
        func: HandlersType,
        filter_: BaseFilter = None,
        as_command: bool = True
):
    """
    Adds a function wrapped in logs and checks from Runner, and sets
    an additional filter on changed messages.
    """

    handler_func = handler_decorator(func)

    if filter_:
        filter_ &= standard_filter
    else:
        filter_ = standard_filter

    if as_command:
        handler_obj = CommandHandler(command, handler_func, filter_, block=False)
    else:
        handler_obj = MessageHandler(filter_, handler_func, block=False)

    bot.add_handler(handler_obj)


async def user_bot_init(token):
    """
    The main function, creates a bot, sets its handlers and starts it.
    """

    bot = Application.builder().token(token).build()

    handler_decorator = Handler.get_decorator("user")
    add_command(bot, handler_decorator, "start", command_start_user, ChatType.PRIVATE)
    add_command(bot, handler_decorator, "generate", command_generate)
    add_command(bot, handler_decorator, "chinese", command_chinese)
    add_command(bot, handler_decorator, "help", command_help_user)
    add_command(bot, handler_decorator, "_", received_message, ChatType.PRIVATE, as_command=False)

    logger("User bot has started")
    print("User bot has started")

    # await bot.updater.start_polling(allowed_updates=[Update.MESSAGE, Update.POLL_ANSWER])
    await bot.initialize()
    await bot.updater.start_polling(allowed_updates=[Update.MESSAGE, Update.POLL_ANSWER])
    await bot.start()


async def admin_bot_init(token):
    """
    The main function, creates a bot, sets its handlers and starts it.
    """

    bot = Application.builder().token(token).build()

    handler_decorator = Handler.get_decorator("admin")
    add_command(bot, handler_decorator, "start", command_start_admin, ChatType.PRIVATE)
    add_command(bot, handler_decorator, "generate", command_generate)
    add_command(bot, handler_decorator, "chinese", command_chinese)
    add_command(bot, handler_decorator, "generate_wat", command_generate_wat)
    add_command(bot, handler_decorator, "generate_absurd", command_generate_absurd)
    add_command(bot, handler_decorator, "lorem", command_lorem)
    add_command(bot, handler_decorator, "translate", command_translate)
    add_command(bot, handler_decorator, "help", command_help_admin)
    add_command(bot, handler_decorator, "_", received_message, ChatType.PRIVATE, as_command=False)

    logger("Admin bot has started")
    print("Admin bot has started")

    await bot.initialize()
    await bot.updater.start_polling(allowed_updates=[Update.MESSAGE, Update.POLL_ANSWER])
    await bot.start()


async def test_bot_init(token):
    """
    The main function, creates a bot, sets its handlers and starts it.
    """

    bot = Application.builder().token(token).build()

    handler_decorator = Handler.get_decorator("test")
    add_command(bot, handler_decorator, "_", received_message, ChatType.PRIVATE, as_command=False)

    logger("Test bot has started")
    print("Test bot has started")

    await bot.initialize()
    await bot.updater.start_polling()
    await bot.start()
