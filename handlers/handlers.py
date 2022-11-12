import re
import random
from typing import List, Union

from telegram import Update
from telegram.ext import CallbackContext

from messages import messages
from lorem_generator import lorem_generator, chinese_generator
from translator import text_translator, shared_languages

from .utils import parse_args, translate, channel_utils


__all__ = [
    "echo",
    "received_message",
    "command_start_user",
    "command_start_admin",
    "command_help_user",
    "command_help_admin",
    "command_generate",
    "command_chinese",
    "command_random",
    "new_channel_post",
    "command_generate_wat",
    "command_generate_absurd",
    "command_lorem",
    "command_translate",
    "repeat_command",
]


async def echo(update: Update, context: CallbackContext) -> str:
    """
    Just an echo function to test the commands.
    """
    print("there!")
    return update.message.text


exclude_letter_pattern = re.compile(r"\W")


async def received_message(update: Update, context: CallbackContext) -> str:
    """
    Bot does not know how to work with messages, so just a stub.
    """

    text = update.message.text
    if text.startswith("/"):
        command_end = exclude_letter_pattern.search(text[1:])
        command_end = (command_end.start() + 1) if command_end else None
        command = text[:command_end]
        message = messages["message"]["unknown"].format(command)
    else:
        message = messages["message"]["default"]
    return message


async def command_start_user(update: Update, context: CallbackContext) -> str:
    """
    Standard welcome for the user bot.
    """
    return messages["start"]["user"]


async def command_start_admin(update: Update, context: CallbackContext) -> str:
    """
    Standard welcome for the admin bot.
    """
    return messages["start"]["admin"]


async def command_help_user(update: Update, context: CallbackContext) -> str:
    """
    Displays either general help or help for a known command. For help
    on the user bot. Usage:
    /help
    /help [/command]
    """

    input_text = update.message.text
    params = parse_args(input_text)

    if not params:
        message = messages["help"]["user"]
    elif params[0] == "/generate":
        message = messages["help"]["generate"]
    elif params[0] == "/chinese":
        message = messages["help"]["chinese"]
    elif params[0] == "/random":
        message = messages["help"]["random"]
    elif params[0] == "/help":
        message = messages["help"]["help"]
    else:
        message = messages["help"]["unknown"].format(params[0])

    return message


async def command_help_admin(update: Update, context: CallbackContext) -> str:
    """
    Displays either general help or help for a known command. For help
    on the admin bot. Usage:
    /help
    /help [/command]
    """

    input_text = update.message.text
    params = parse_args(input_text)

    if not params:
        message = messages["help"]["admin"]
    elif params[0] == "/generate":
        message = messages["help"]["generate"]
    elif params[0] == "/chinese":
        message = messages["help"]["chinese"]
    elif params[0] == "/generate_wat":
        message = messages["help"]["generate_wat"]
    elif params[0] == "/generate_absurd":
        message = messages["help"]["generate_absurd"]
    elif params[0] == "/lorem":
        languages = ", ".join(lorem_generator.languages)
        message = messages["help"]["lorem"].format(languages=languages)
    elif params[0] == "/translate":
        translator_names = ", ".join(text_translator.translator_names)
        languages = ", ".join(shared_languages)
        message = messages["help"]["translate"].format(
            translators=translator_names,
            languages=languages
        )
    elif params[0] == "/help":
        message = messages["help"]["help"]
    else:
        message = messages["help"]["unknown"].format(params[0])

    return message


async def command_generate(update: Update, context: CallbackContext) -> str:
    """
    Generates a small phrase in Russian via lorem and then translates it
    using LingvaNex as Bulgarian.
    Usage:
    /generate
    """

    word_count = random.randint(5, 16)
    text = lorem_generator("ru", word_count, chars_len=2)
    message, _ = await translate(text, "lin", "bg", "ru")
    return message


async def command_chinese(update: Update, context: CallbackContext) -> str:
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
    return message


async def command_random(update: Update, context: CallbackContext):
    """
    Forwards a random message from the channel to the user who requested
    it.
    Usage:
    /random
    """
    return await channel_utils.reply_random_post(update.effective_chat)


async def new_channel_post(update: Update, context: CallbackContext):
    """
    Handler for posts from the channel.
    Updates the last channel post id to pick random posts more
    correctly.
    """
    channel_utils.set_last_id(update.channel_post.message_id)


async def command_generate_wat(update: Update, context: CallbackContext) -> str:
    """
    Generates a small phrase in Russian via lorem and then translates it
    using IBM Watson as Ukrainian.
    Generation is done by the algorithm [wat:uk-en + lin:en-ru] because
    it has better results. Also, all punctuation marks are ignored.
    Usage (in admin version):
    /generate_wat
    """

    word_count = random.randint(10, 18)
    text = lorem_generator("ru", word_count, chars_len=2)
    text = lorem_generator.clear_text(text)
    text, succ = await translate(text, "wat", "uk", "en")
    if succ:
        text, _ = await translate(text, "lin", "en", "ru")
    return text


async def command_generate_absurd(update: Update, context: CallbackContext) -> str:
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
        text, succ = await translate(text, "lin", language, to_language)
        if not succ:
            break
        language = to_language
    else:
        # translated without errors, translate the current text into Russian
        if language != "ru":
            text, _ = await translate(text,  "lin", language, "ru")

    return text


async def command_lorem(update: Update, context: CallbackContext) -> str:
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
        # incorrect parameters
        message = input_params
    else:
        lorem = lorem_generator.generate_lorem(*input_params)
        message = lorem_generator.clear_text(lorem)

    return message


async def command_translate(update: Update, context: CallbackContext) -> str:
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

    return message


async def repeat_command(update: Update, context: CallbackContext) -> Union[str, Update]:
    """
    Just repeats the command from the replay.
    The command must be a message starting with "/".
    Usage (in admin version):
    + [reply: /lorem en 56]
    """

    if (
            not update.message.reply_to_message
            or not update.message.reply_to_message.text
    ):
        return messages["plus"]["no_reply"]

    if not update.message.reply_to_message.text.startswith("/"):
        return messages["plus"]["no_command"]

    # Moving the reply to the message and clearing cache
    update.message = update.message.reply_to_message
    update.message.reply_to_message = None
    update._effective_message = None
    return update
