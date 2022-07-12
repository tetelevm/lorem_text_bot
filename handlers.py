import re
from functools import wraps
from typing import Callable

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from logger import logger, error_logger
from messages import messages
from lorem_generator import lorem_generator


__all__ = [
    "received_message",
    "command_start",
    "command_help",
    "command_lorem",
    "command_translation",
    "command_translorem",
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
            func(update, context)
        except Exception as exc:
            error_logger.error(error_logger.get_full_exc_info(exc))
            logger.error(logger.get_exc_info(exc))
            update.effective_chat.send_message(messages["error"])
    return wrapper


repeated_spaces_pattern = re.compile(r"[\s]+")

def get_params(text: str) -> list[str]:
    """
    Parses query arguments: splits by spaces and returns everything after
    the first (the command proper).
    """

    text = repeated_spaces_pattern.sub(" ", text)
    params = text.strip().split(" ")
    return params[1:]


# =====================================================================


@handler
def received_message(update: Update, context: CallbackContext):
    """
    Bot does not know how to work with messages, so just a stub.
    """
    update.effective_chat.send_message(messages["message"])


@handler
def command_start(update: Update, context: CallbackContext):
    """
    Standard welcome.
    """
    update.effective_chat.send_message(
        messages["start"],
        parse_mode=ParseMode.MARKDOWN
    )


@handler
def command_help(update: Update, context: CallbackContext):
    """
    Displays either general help or help for a known command. Usage:
    /help
    /help /command
    """

    input_text = update.message.text
    params = get_params(input_text)

    if not params:
        message = messages["help"]["default"]
    elif params[0] in ["/help", "/lorem", "/translation", "/translorem"]:
        message = messages["help"][params[0][1:]]
    else:
        message = messages["help"]["unknown"].format(params[0])

    update.effective_chat.send_message(
        message,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )


@handler
def command_lorem(update: Update, context: CallbackContext):
    """
    Returns a lorem-like pseudo-text that looks like a real language.
    Has 2 optional positional integer arguments - `word count` (5-256)
    and `characters count` (1-3). Usage:
    /lorem
    /lorem 128
    /lorem 128 3
    """

    def get_response(word_count: str = None, chars_len: str = None, *args) -> str:
        """
        Parses arguments to generate and generates pseudotext.
        """

        # parse word_count
        if word_count is None:
            word_count = lorem_generator.default_word_count
        else:
            try:
                word_count = int(word_count)
            except ValueError:
                return messages["lorem"]["word_error"].format(word_count)
        if not (5 <= word_count <= 256):
            return messages["lorem"]["word_count"].format(word_count)

        # parse chars_len
        if chars_len is None:
            chars_len = lorem_generator.default_chars_len
        else:
            try:
                chars_len = int(chars_len)
            except ValueError:
                return messages["lorem"]["chars_error"].format(chars_len)
        if not (1 <= chars_len <= 3):
            return messages["lorem"]["chars_count"].format(chars_len)

        # generate lorem
        lorem = lorem_generator.generate_lorem(word_count, chars_len)
        return lorem

    input_text = update.message.text
    params = get_params(input_text)
    message = get_response(*params)
    update.effective_chat.send_message(message)


@handler
def command_translation(update: Update, context: CallbackContext):
    """
    Feature in development.
    """
    update.effective_chat.send_message(messages["todo"])


@handler
def command_translorem(update: Update, context: CallbackContext):
    """
    Feature in development.
    """
    update.effective_chat.send_message(messages["todo"])
