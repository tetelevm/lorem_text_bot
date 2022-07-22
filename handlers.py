import re
from functools import wraps
from typing import Callable, List, Tuple, Union

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from logger import logger, error_logger
from messages import messages
from lorem_generator import lorem_generator
from translator import translators, TranslationTimeoutException, TranslationRequestException


__all__ = [
    "received_message",
    "command_start",
    "command_help",
    "command_lorem",
    "command_translation",
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

def get_params(text: str) -> List[str]:
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
        parse_mode=ParseMode.HTML
    )


@handler
def command_help(update: Update, context: CallbackContext):
    """
    Displays either general help or help for a known command. Usage:
    /help
    /help [/command]
    """

    input_text = update.message.text
    params = get_params(input_text)

    if not params:
        message = messages["help"]["default"]
    elif params[0] == "/lorem":
        languages = ", ".join(lorem_generator.text_data)
        message = messages["lorem"]["help"].format(languages=languages)
    elif params[0] in ["/help", "/translation"]:
        message = messages[params[0][1:]]["help"]
    else:
        message = messages["help"]["unknown"].format(params[0])

    update.effective_chat.send_message(
        message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


@handler
def command_lorem(update: Update, context: CallbackContext):
    """
    Returns a lorem-like pseudo-text that looks like a real language.
    Has 2 optional positional integer arguments - `word count` (5-256)
    and `characters count` (1-3). Usage:
    /lorem [lang] [words [chars]]
    /lorem
    /lorem en
    /lorem 128
    /lorem en 128
    /lorem 128 3
    /lorem en 128 3
    """

    def parse_args(
            language: str = "",
            word_count: str = "",
            char_count: str = "",
            *args
    ) -> Union[Tuple[str, int, int], str]:
        """
        Parses and validates the first three passed arguments.
        The first can be language or word count (in this case a number),
        the second word count or character count (depends on the first),
        the third only character count.
        The generation language must be known, the word count between
        5 and 256, the character count between 1 and 3.
        If all is normal, it will return a list of three generation
        parameters, if there is an error, it will return a string.
        """
        returned_params = [
            lorem_generator.default_language,
            lorem_generator.default_word_count,
            lorem_generator.default_chars_len
        ]
        params = [language, word_count, char_count]
        if params[0].isdecimal():
            # params0 is word count
            params = [lorem_generator.default_language, params[0], params[1]]

        # parse
        if params[0]:
            returned_params[0] = params[0]
        if params[1]:
            try:
                returned_params[1] = int(params[1])
            except ValueError:
                return messages["lorem"]["word_error"].format(params[1])
        if params[2]:
            try:
                returned_params[2] = int(params[2])
            except ValueError:
                return messages["lorem"]["char_error"].format(params[2])

        # validate
        if returned_params[0] not in lorem_generator.text_data:
            return messages["lorem"]["lang_error"].format(returned_params[0])
        if not 5 <= returned_params[1] <= 256:
            return messages["lorem"]["word_count"].format(returned_params[1])
        if not 1 <= returned_params[2] <= 3:
            return messages["lorem"]["char_count"].format(returned_params[2])

        return (returned_params[0], returned_params[1], returned_params[2])

    input_text = update.message.text
    args = get_params(input_text)
    input_params = parse_args(*args)
    if isinstance(input_params, str):
        message = input_params
    else:
        message = lorem_generator.generate_lorem(*input_params)

    update.effective_chat.send_message(message, parse_mode=ParseMode.HTML)


@handler
def command_translation(update: Update, context: CallbackContext):
    """
    Feature in development.
    """
    update.effective_chat.send_message(messages["todo"])
