from functools import wraps
from typing import Callable

import asyncio
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import (
    Updater,
    CommandHandler,
    Dispatcher,
    MessageHandler,
    Filters,
    BaseFilter,
)

from logger import logger, error_logger
from messages import messages
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
    "bot_main",
]


def handler(func: Callable):
    """
    Decorator for handlers. Logs requests and catches errors.
    When crashes, it writes logs to a special file and outputs a
    standard error message.
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        logger.info(f"   Req >>| {logger.flatten_string(update.message.text)}")
        try:
            asyncio.run(func(update, context))
        except Exception as exc:
            error_logger.error(error_logger.get_full_exc_info(exc))
            logger.error(logger.get_exc_info(exc))
            update.effective_chat.send_message(messages["error"])

    return wrapper


class NoChangeFilter(BaseFilter):
    """
    Filter for new messages only, edited messages are ignored.
    """
    __slots__ = ()
    def __call__(self, update: Update) -> bool:
        return bool(update.message)

no_change_filter = NoChangeFilter()


standard_filter = no_change_filter & Filters.text


def add_all_handlers(dispatcher: Dispatcher):
    """
    Adds all existing handlers to the bot.
    """

    def add_command(command: str, func: Callable, *args):
        """
        Adds a function as a handler, additionally sets a filter on
        changed messages.
        """
        func = handler(func)

        args = list(args)
        if args:
            args[0] &= standard_filter
        else:
            args.append(standard_filter)

        dispatcher.add_handler(CommandHandler(command, func, *args))

    add_command("start", command_start, Filters.chat_type.private)
    add_command("generate_absurd", command_generate_absurd)
    add_command("generate", command_generate)
    add_command("chinese", command_chinese)
    add_command("lorem", command_lorem)
    add_command("translate", command_translate)
    add_command("help", command_help)

    dispatcher.add_handler(MessageHandler(
        Filters.chat_type.private & standard_filter,
        handler(received_message)
    ))


def bot_main(token):
    """
    The main function, creates a bot, sets its handlers and starts it.
    """

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    add_all_handlers(dispatcher)
    updater.start_polling()
    logger("Bot has started")
    print("Bot has started")
    updater.idle()
