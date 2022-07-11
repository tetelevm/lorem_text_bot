import re

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from lorem_generator import lorem_generator


__all__ = [
    "received_message",
    "command_start",
    "command_help",
    "command_lorem",
    "command_translation",
    "command_translorem",
]


messages = {
    "message": (
        "🖐️ Привет!\n"
        "🤖 Я всего лишь глупый робот, который не понимает слов.\n"
        "❓ Мои команды описаны в справке /help"
    ),
    "start": (
        "🖐 Привет! Вот мои команды:\n"
        "📃 /lorem - сгенерировать *псевдотекст*\n"
        "🈲 /trans - *перевод* рандомного китайского текста\n"
        "📰 /translorem - попытка *перевода псевдотекста*\n"
        "🧐 /help - *справка* (более подробно и со ссылкой на документацию)"
    ),

    "help": {
        "default": (
            "❓ Я - бот для генерации псевдотекстов 🤖. Я знаю команды:\n\n"
            "📃 /lorem - по определённому алгоритму создаю *текст с бессмысленными"
            " словами*, который по звучанию похож на русский, но по факту lorem\n\n"
            "🈲 /trans - беру *случайные китайские символы* и отправляю переводчику"
            " на переваривание (иногда переводчик ведётся на такое)\n\n"
            "📰 /translorem - генерирую *псевдотекст*, а затем пытаюсь подсунуть"
            " его *переводчику* как настоящий текст на редком языке\n\n"
            "🧐 /help - выводит это сообщение\n\n"
            "🤓 Если хочешь описание подробнее, то вызови <`/help [команда]`>"
            " (например <`/help /lorem`>)\n\n"
            "Исходники и собранная воедино справка <[лежат тут]"
            "(https://github.com/tetelevm/lorem_text_bot)> 🐙.Там же можно"
            " спросить вопросов."
        ),
        "help": "🪲❓ Произошла рекурсия, не делайте так!",
        "lorem": (
            "📃 /lorem генерирует *псевдотекст*.\n\n"
            "🧠 *Алгоритм* такой, что рандомно выбираются дополняющие друг друга"
            " символы из существующего текста.\n"
            "Для этого для __последних символов__ в строке ищется их случайное"
            " расположение в исходном тексте. Затем в текст лорема добавляются"
            " __следующие символы__ за ними. А дальше они становятся новыми"
            " символами, которые ищутся в строке.\n"
            "Чем больше берётся символов, тем более похож текст на реальный"
            " язык.\n\n"
            "🪛 Вызов имеет два параметра:\n"
            "- количество сгенерированных слов (по умолчанию 48, варианты 32-256)\n"
            "- количество последних символов (по умолчанию 2, варианты 1-3)\n\n"
            "📗Примеры: <`/lorem`> <`/lorem 128`> <`/lorem 64 1`>"
        ),
        "translation": "# TODO",
        "translorem": "# TODO",
        "unknown": "🔎 Ищем-ищем... Не нашли справки для `<{}>`.",
    },

    "lorem": {
        "word_error": "🪲 Ошибка! Непонятное количество слов `<{}>`.",
        "word_count": "🪲 Ошибка! Количество слов должно быть 5-256, у вас `<{}>`.",
        "chars_error": "🪲 Ошибка! Непонятное количество символов `<{}>`.",
        "chars_count": "🪲 Ошибка! Количество символов должно быть 1-3, у вас `<{}>`.",
    },

    "todo": "💻 Функционал ещё не готов, пытаемся реализовать.",
}


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


def received_message(update: Update, context: CallbackContext):
    """
    Bot does not know how to work with messages, so just a stub.
    """
    update.effective_chat.send_message(
        messages["message"],
        parse_mode=ParseMode.MARKDOWN
    )


def command_start(update: Update, context: CallbackContext):
    """
    Standard welcome.
    """
    update.effective_chat.send_message(
        messages["start"],
        parse_mode=ParseMode.MARKDOWN
    )


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


def command_lorem(update: Update, context: CallbackContext):
    """
    Returns a lorem-like pseudo-text that looks like a real language.
    Has 2 optional positional integer arguments - `word count` and
    `characters count`. Usage:
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
    update.effective_chat.send_message(message, parse_mode=ParseMode.MARKDOWN)


def command_translation(update: Update, context: CallbackContext):
    """
    Feature in development.
    """
    update.effective_chat.send_message(messages["todo"])


def command_translorem(update: Update, context: CallbackContext):
    """
    Feature in development.
    """
    update.effective_chat.send_message(messages["todo"])
