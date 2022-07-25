__version__ = "0.8"

from typing import Callable

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    Dispatcher,
    MessageHandler,
    Filters,
    BaseFilter,
)

from envs import envs
from logger import logger
from handlers import (
    received_message,
    command_start,
    command_help,
    command_lorem,
    command_translate,
    command_generate,
)


if envs.get("DEBUG", False):
    # test bot for development
    TOKEN = envs["TOKEN_TEST"]
else:
    TOKEN = envs["TOKEN"]


class NoChangeFilter(BaseFilter):
    """
    Filter for new messages only, edited messages are ignored.
    """
    __slots__ = ()
    def __call__(self, update: Update) -> bool:
        return bool(update.message)

no_change_filter = NoChangeFilter()


def add_all_handlers(dispatcher: Dispatcher):
    """
    Adds all existing handlers to the bot.
    """

    def add_command(command: str, func: Callable, *args, **kwargs):
        """
        Adds a function as a handler, additionally sets a filter on
        changed messages.
        """
        args = list(args)
        if args:
            args[0] &= standard_filters
        elif "filters" in kwargs:
            kwargs["filters"] &= standard_filters
        else:
            args.append(standard_filters)
        dispatcher.add_handler(CommandHandler(command, func, *args, **kwargs))

    standard_filters = no_change_filter & Filters.text

    add_command("start", command_start, Filters.chat_type.private)
    add_command("help", command_help)
    add_command("lorem", command_lorem)
    add_command("translate", command_translate)
    add_command("generate", command_generate)

    dispatcher.add_handler(MessageHandler(
        Filters.chat_type.private & standard_filters,
        received_message
    ))


def main():
    """
    The main function, creates a bot, sets its handlers and starts it.
    """

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    add_all_handlers(dispatcher)
    updater.start_polling()

    print("Bot has started")
    logger("Bot has started")
    updater.idle()


if __name__ == '__main__':
    main()
