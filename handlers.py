import re
import random
from typing import List, Union, Tuple

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from messages import messages
from lorem_generator import lorem_generator, chinese_generator
from translator import (
    text_translator,
    shared_languages,
    TranslationTimeoutException,
    TranslationRequestException,
)


__all__ = [
    "received_message",
    "command_start",
    "command_help",
    "command_lorem",
    "command_translate",
    "command_generate",
    "command_generate_absurd",
    "command_chinese",
]


repeated_spaces_pattern = re.compile(r"[\s]+")

def parse_args(text: str) -> List[str]:
    """
    Parses query arguments: splits by spaces and returns everything after
    the first (the command proper).
    """

    text = repeated_spaces_pattern.sub(" ", text)
    params = text.strip().split(" ")
    return params[1:]


async def translate(text: str, *params) -> Tuple[str, bool]:
    """
    Makes a translation and catches errors. Returns 2 arguments - the
    text and the success of the translation.
    """

    try:
        result = await text_translator(text, *params)
        return result, True
    except TranslationTimeoutException:
        return messages["translate"]["timeout_error"], False
    except TranslationRequestException:
        return messages["translate"]["request_error"], False


# =====================================================================


no_letter_pattern = re.compile(r"\W")

async def received_message(update: Update, context: CallbackContext):
    """
    Bot does not know how to work with messages, so just a stub.
    """
    text = update.message.text
    if text.startswith("/"):
        command_end = no_letter_pattern.search(text[1:])
        command_end = (command_end.start() + 1) if command_end else None
        command = text[:command_end]
        message = messages["message"]["unknown"].format(command)
    else:
        message = messages["message"]["default"]
    update.effective_chat.send_message(message, parse_mode=ParseMode.HTML)


async def command_start(update: Update, context: CallbackContext):
    """
    Standard welcome.
    """
    update.effective_chat.send_message(
        messages["start"],
        parse_mode=ParseMode.HTML
    )


async def command_help(update: Update, context: CallbackContext):
    """
    Displays either general help or help for a known command. Usage:
    /help
    /help [/command]
    """

    input_text = update.message.text
    params = parse_args(input_text)

    if not params:
        message = messages["help"]["default"]
    elif params[0] == "/lorem":
        languages = ", ".join(lorem_generator.languages)
        message = messages["lorem"]["help"].format(languages=languages)
    elif params[0] == "/translate":
        translator_names = ", ".join(text_translator.translator_names)
        shared = ", ".join(shared_languages)
        message = messages["translate"]["help"].format(
            translators=translator_names,
            shared=shared
        )
    elif params[0] == "/generate":
        message = messages["generate"]["help"]
    elif params[0] == "/generate_absurd":
        message = messages["generate_absurd"]["help"]
    elif params[0] == "/chinese":
        message = messages["chinese"]["help"]
    elif params[0] == "/help":
        message = messages["help"]["help"]
    else:
        message = messages["help"]["unknown"].format(params[0])

    update.effective_chat.send_message(
        message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


async def command_lorem(update: Update, context: CallbackContext):
    """
    Returns a lorem-like pseudo-text that looks like a real language.
    Has 3 optional positional integer arguments - `language`,
    `word count` (5-256) and `characters count` (1-3). Usage:
    /lorem [lang] [words [chars]]
    /lorem
    /lorem en
    /lorem 128
    /lorem en 128
    /lorem 128 3
    /lorem en 128 3
    """

    def get_params(
            language: str = "",
            word_count: str = "",
            char_count: str = "",
            *args
    ) -> Union[list, str]:
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
        if returned_params[0] not in lorem_generator.languages:
            return messages["lorem"]["lang_error"].format(returned_params[0])
        if not 5 <= returned_params[1] <= 256:
            return messages["lorem"]["word_count"].format(returned_params[1])
        if not 1 <= returned_params[2] <= 3:
            return messages["lorem"]["char_count"].format(returned_params[2])

        return returned_params

    input_text = update.message.text
    args = parse_args(input_text)
    input_params = get_params(*args)
    if isinstance(input_params, str):
        message = input_params
    else:
        message = lorem_generator.generate_lorem(*input_params)

    update.effective_chat.send_message(message, parse_mode=ParseMode.HTML)


async def command_translate(update: Update, context: CallbackContext):
    """
    A command to translate text from one language to another.
    Uses a third-party translation service.
    Has three launch commands: translator, language_from and language_to.
    Usage:
    /translate [translator] [from [to]]
    /translate
    /translate lin
    /translate uk
    /translate en ja
    /translate lin de fi
    """

    def check_text() -> str:
        """
        Checks if there is a message in the reply and if there is text
        in it.
        """
        if not update.message.reply_to_message:
            return messages["translate"]["no_reply"]
        if not update.message.reply_to_message.text:
            return messages["translate"]["no_reply_text"]
        return ""

    def get_params(
            translator_name: str = "",
            from_lang: str = "",
            to_lang: str = "",
            *args
    ) -> Union[List[str], str]:
        """
        Parses query parameters.
        It has three parameters - translator and translation languages.
        The translator must be known (languages, too, but they are
        different for different translators).
        """
        returned_params = [
            text_translator.defaults_translator,
            text_translator.default_from,
            text_translator.default_to,
        ]
        params = [translator_name, from_lang, to_lang]
        if len(params[0]) != 3:
            # no translator specified
            params = [returned_params[0], params[0], params[1]]
        if params[0] not in text_translator.translator_names:
            return messages["translate"]["translator_error"].format(params[0])

        for param_ind in range(3):
            if params[param_ind]:
                returned_params[param_ind] = params[param_ind]
        return returned_params

    message = check_text()
    if not message:
        args = parse_args(update.message.text)
        params = get_params(*args)
        if isinstance(params, str):
            message = params
        else:
            text = update.message.reply_to_message.text
            message, _ = await translate(text, *params)
    update.effective_chat.send_message(message, parse_mode=ParseMode.HTML)


async def command_generate(update: Update, context: CallbackContext):
    """
    Generates a small phrase in Russian via lorem and then translates it
    using IBM Watson as Ukrainian.
    Usage:
    /generate
    """

    text = lorem_generator("ru", 16, 2)
    message, _ = await translate(text, "wat", "uk", "ru")
    update.effective_chat.send_message(message, parse_mode=ParseMode.HTML)


async def command_generate_absurd(update: Update, context: CallbackContext):
    """
    Generates a lorem with random parameters, then translates to other
    languages a random number of times and displays the translation in
    Russian.
    Usage:
    /generate_absurd
    """

    lorem_params = [
        random.choice(lorem_generator.languages),
        random.randint(32, 128),
        random.randint(1, 3)
    ]
    language = lorem_params[0]
    text = lorem_generator(*lorem_params)

    # a few translations through different languages
    count = random.randint(1, 3)
    for _ in range(count):
        to_language = random.choice([
            lang
            for lang in shared_languages
            if lang != language
        ])
        translator = random.choice(text_translator.translator_names)
        text, succ = await translate(text, translator, language, to_language)
        if not succ:
            break
        language = to_language
    else:
        # translated without errors, translate the current text into Russian
        if language != "ru":
            translator = random.choice(text_translator.translator_names)
            text, _ = await translate(text, translator, language, "ru")

    update.effective_chat.send_message(text, parse_mode=ParseMode.HTML)


async def command_chinese(update: Update, context: CallbackContext):
    """
    Takes a random number of Chinese characters (in the range of 8-24)
    from a large set and translates them into Russian. It turns out
    interesting.
    Usage:
    /chinese
    """

    count = random.randint(8, 24)
    ch_text = chinese_generator.get_chinese(count)
    message, _ = await translate(ch_text, "lin", "zh-Hans_CN", "ru")
    update.effective_chat.send_message(message, parse_mode=ParseMode.HTML)
