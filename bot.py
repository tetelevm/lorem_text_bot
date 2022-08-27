from typing import Callable

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import BaseFilter, ChatType, TEXT

from logger import logger
from handlers import (
    received_message,
    command_start,
    command_help,
    command_lorem,
    command_translate,
    command_generate,
    command_generate_absurd,
    command_chinese,
)


__all__ = [
    "bot_init",
]


class NoChangeFilter(BaseFilter):
    """
    Filter for new messages only, edited messages are ignored.
    """
    def __call__(self, update: Update) -> bool:
        return bool(update.message)

no_change_filter = NoChangeFilter()


standard_filter = no_change_filter & TEXT


def add_all_handlers(bot: Application):
    """
    Adds all existing handlers to the bot.
    """

    def add_command(command: str, func: Callable, *args):
        """
        Adds a function wrapped in logs and checks from Runner, and sets
        an additional filter on changed messages.
        """

        args = list(args)
        if args:
            args[0] &= standard_filter
        else:
            args.append(standard_filter)

        com_handler = CommandHandler(command, func, *args, block=False)
        bot.add_handler(com_handler)

    add_command("start", command_start, ChatType.PRIVATE)
    add_command("generate_absurd", command_generate_absurd)
    add_command("generate", command_generate)
    add_command("chinese", command_chinese)
    add_command("lorem", command_lorem)
    add_command("translate", command_translate)
    add_command("help", command_help)

    bot.add_handler(MessageHandler(
        ChatType.PRIVATE & standard_filter,
        received_message,
        block=False
    ))


def bot_init(token):
    """
    The main function, creates a bot, sets its handlers and starts it.
    """

    bot = Application.builder().token(token).build()
    add_all_handlers(bot)
    logger("Bot has started")
    print("Bot has started")
    bot.run_polling()
