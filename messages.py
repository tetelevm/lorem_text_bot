from typing import TypedDict


__all__ = [
    "messages",
]


_Message = TypedDict("_Message", {
    "default": str,
    "unknown": str,
})
_Start = TypedDict("_Start", {
    "user": str,
    "admin": str,
})
_Lorem = TypedDict("_Lorem", {
    "word_error": str,
    "char_error": str,
    "lang_error": str,
    "word_count": str,
    "char_count": str,
})
_Translate = TypedDict("_Translate", {
    "no_reply": str,
    "no_reply_text": str,
    "translator_error": str,
    "timeout_error": str,
    "request_error": str,
})
_Help = TypedDict("_Help", {
    "user": str,
    "admin": str,
    "generate": str,
    "chinese": str,
    "generate_wat": str,
    "generate_absurd": str,
    "lorem": str,
    "translate": str,
    "help": str,
    "unknown": str,
})

_Messages = TypedDict(
    "_Messages",
    {
        "already_run": str,
        "error": str,
        "todo": str,
        "message": _Message,
        "start": _Start,
        "lorem": _Lorem,
        "translate": _Translate,
        "help": _Help,
    }
)

_github_link = "https://github.com/tetelevm/lorem_text_bot"


messages: _Messages = {
    "already_run": "🕓 Я уже думаю над задачей выше, дождитесь её выполнения.",
    "error": "🪲 500 🪲 На сервере произошла какая-то ошибка, уже чиним!",
    "todo": "💻 Функционал ещё не готов, пытаемся реализовать.",

    "message": {
        "default": (
            "🤖 Я всего лишь глупый робот, который не понимает слов.\n"
            "❓ Мои команды описаны в справке /help"
        ),
        "unknown": (
            "🔎 Хмм, не знаю команду &lt;<code>{}</code>&gt;\n"
            "❓ Мои команды описаны в справке /help"
        ),
    },

    "start": {
        "user": (
            "🖐 Привет! Вот мои команды:\n"
            "\n"
            "🅰️ /generate - сгенерировать <b>фразу</b>\n"
            "🈲️ /chinese - перевести случайные <b>китайские символы</b>\n"
            "🧐 /help - <b>справка</b> (более подробное описание)"
        ),
        "admin": (
            "🖐 Привет! Вот мои <b>админские</b> команды:\n"
            "\n"
            "🅰️ /generate - сгенерировать <b>фразу</b>\n"
            "🈲️ /chinese - перевести случайные <b>китайские символы</b>\n"
            "🇼️ /generate_wat - сгенерировать <b>фразу</b> через Watson\n"
            "🔤 /generate_absurd - сгенерировать немного <b>абсурдоткекста</b>\n"
            "📃 /lorem - сгенерировать <b>псевдотекст</b>\n"
            "🔄 /translate - <b>перевод</b> текста по реплаю сообщения\n"
            "🧐 /help - <b>справка</b> (более подробное описание)"
        ),
    },

    "lorem": {
        "word_error": "🐞 Непонятное количество слов &lt;<code>{}</code>&gt;.",
        "char_error": "🐞 Непонятное количество символов &lt;<code>{}</code>&gt;.",
        "lang_error": (
            "🐞 Неизвестный язык &lt;<code>{}</code>&gt;. Языки, на которых я умею"
            " генерировать лорем, вы можете посмотреть командой &lt;<code>/help /lorem</code>&gt;."
        ),
        "word_count": "🐞 Количество слов должно быть 5-256, у вас &lt;<code>{}</code>&gt;.",
        "char_count": "🐞 Количество символов должно быть 1-3, у вас &lt;<code>{}</code>&gt;.",
    },

    "translate": {
        "no_reply": "🐞 Переводы работают только с ответами сообщений.",
        "no_reply_text": "🐞 В сообщении из ответа нет текста, не могу перевести.",
        "translator_error": (
            "🐞 Неизвестный переводчик &lt;<code>{}</code>&gt;. Переводчикии, которыми я умею"
            " переводить, вы можете посмотреть командой &lt;<code>/help /translate</code>&gt;."
        ),
        "timeout_error": (
            "🐞 Сервер слишком долго не отвечает, запрос перевода оборван. Скорее всего, сервер"
            " просто завис при запросе или заснул при переводе. Попробуйте повторить."
        ),
        "request_error": (
            "🐞 Ошибка при запросе. Возможно, неизвестный переводчику язык, сервер прилёг поспать"
            "или какая-то другая непонятная причина."
        ),
    },

    "help": {
        "user": (
            "❓ Я - бот для генерации псевдотекстов 🤖. Я знаю команды:\n"
            "\n"
            "🅰️ /generate - <b>генерирую абсурдную фразу</b> с использованием лорема и переводом"
            " с болгарского\n"
            "\n"
            "🈲 /chinese - беру случайное количество <b>китайских символов</b> и перевожу их\n"
            "\n"
            "🧐 /help - выводит это сообщение\n"
            "\n"
            "🤓 Более подробное описание:\n"
            "<code>/help /generate</code>\n"
            "<code>/help /chinese</code>\n"
            "\n"
            + f"Исходники &lt;<a href=\"{_github_link}\">тут</a>&gt; 🐙."
        ),

        "admin": (
            "❓ Я - <b>админский</b> бот для генерации псевдотекстов 🤖. Я знаю команды"
            " (* - доступные только в админской версии):\n"
            "\n"
            "🅰️ /generate - <b>генерирую абсурдную фразу</b> с использованием лорема и переводом"
            " с болгарского\n"
            "\n"
            "🈲 /chinese - беру случайное количество <b>китайских символов</b> и перевожу их\n"
            "\n"
            "* 🇼️ /generate_wat - <b>генерирую абсурдную фразу</b> с использованием лорема и"
            "переводом с украинского\n"
            "\n"
            "* 🔤 /generate_absurd - <b>генерирую абсурдотекст</b> с использованием лорема и"
            " переводом\n"
            "\n"
            "* 📃 /lorem - по определённому алгоритму создаю <b>текст с бессмысленными словами</b>,"
            " который по звучанию похож на русский, но по факту лорем\n"
            "\n"
            "* 🔄 /translate - работаю по реплаю на сообщения: <b>беру его текст</b> и отправляю"
            " одному из переводчиков на перевод\n"
            "\n"
            "🧐 /help - выводит это сообщение\n"
            "\n"
            "🤓 Вызови &lt;<code>/help [команда]</code>&gt;, если хочешь подробное описание:\n"
            "<code>/help /generate</code>\n"
            "<code>/help /chinese</code>\n"
            "<code>/help /generate_wat</code>\n"
            "<code>/help /generate_absurd</code>\n"
            "<code>/help /lorem</code>\n"
            "<code>/help /translate</code>\n"
            "\n"
            + f"Исходники &lt;<a href=\"{_github_link}\">лежат тут</a>&gt; 🐙. Там же можно спросить"
            " вопросов."
        ),

        "generate": (
            "🅰️ /generate генерирует случайную фразу абсурда\n"
            "\n"
            "🧠 Суть работы в том, что бот генерирует <b>одно предложение лорема</b> и <b>переводит"
            " его</b> как болгарский язык с помощью LingvaNex.\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/generate</code>&gt; - генерирует рандомную фразу"
        ),

        "chinese": (
            "🔤 /chinese выдаёт перевод случайных китайских символов\n"
            "\n"
            "🧠 Имеется некоторый (довольно большой) набор символов на китайском. Бот берёт из них"
            " случайное количество символов и переводит их. Переводчик думает, что это реальный"
            " текст и реально его переводит.\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/chinese</code>&gt; - переводит китайские символы"
        ),

        "generate_wat": (
            "🇼 /generate_wat генерирует случайную фразу абсурда\n"
            "\n"
            "🧠 Суть работы в том, что бот генерирует <b>одно предложение лорема</b> и <b>переводит"
            " его</b> как украинский язык с помощью IBM Watson.\n"
            "\n"
            "🪛 Не поддерживает параметров.\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/generate</code>&gt; - генерирует рандомную фразу"
        ),

        "generate_absurd": (
            "🔤 /generate_absurd случайным образом генерирует абсурдотекст\n"
            "\n"
            "🧠 Суть работы в том, что бот <b>генерирует лорем</b> (который <code>/lorem</code>) со"
            " случайными параметрами и случайно <b>переводит его</b> (как <code>/translate</code>)"
            " несколько раз на другие языки (и в конце на русский).\n"
            "\n"
            "🪛 Не поддерживает параметров.\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/generate_absurd</code>&gt; - генерирует абсурдотекст"
        ),

        "lorem": (
            "📃 /lorem генерирует <b>псевдотекст</b>.\n"
            "\n"
            "🧠 <b>Алгоритм</b> такой, что рандомно выбираются дополняющие друг друга символы из"
            " существующего текста.\n"
            "Для этого для берётся <i>несколько символов</i> в строке (буфер) и  добавляются в"
            " результирующий текст. Затем ищется их случайное расположение в исходном тексте и"
            " берутся <i>следующие символы</i> за ними, которые и становятся новым буфером.\n"
            "Чем больше буфер, тем более похож текст на реальный язык.\n"
            "\n"
            "🪛 Вызов имеет три параметра:\n"
            "<code>/lorem [язык] [слов [буфер]]</code>\n"
            "- <b>язык текста</b>: по умолчанию используется русский, доступны языки"
            " &lt;{languages}&gt;; параметр можно не указывать\n"
            "- <b>количество сгенерированных слов</b>: по умолчанию 64, варианты 32-256\n"
            "- <b>длина буфера</b>: по умолчанию 2, варианты 1-3\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/lorem</code>&gt; - стандартная генерация 64 слов на русском\n"
            "- &lt;<code>/lorem 128</code>&gt; - генерация 128 слов\n"
            "- &lt;<code>/lorem 64 1</code>&gt; - генерация 64 слов с буфером 1\n"
            "- &lt;<code>/lorem el 32</code>&gt; - генерация 32 слов на греческом\n"
            "- &lt;<code>/lorem en 48 3</code>&gt; - генерация 48 слов на английском с буфером 3\n"
        ),
        "translate": (
            "🔄 /translate переводит текст с помощью переводчика с одного языка на другой\n"
            "\n"
            "🧠 Для работы надо <b>ответить на сообщение</b> (своё или бота) и вызвать в ответе"
            " команду <code>/translate</code>. Бот перешлёт <i>текст этого сообщения</i> на"
            " перевод одному из переводчиков.\n"
            "\n"
            "🪛 Поддерживает три параметра:\n"
            "<code>/translate [translator] [from [to]]</code>\n"
            "- <b>translator</b>: переводчик, с помощью которого происходит перевод; доступны"
            " значения <i>{translators}</i>, по умолчанию <i>wat</i>\n"
            "- <b>from</b>: язык, с которого происходит перевод; по умолчанию просто отдаёт на"
            " распознание переводчиком\n"
            "- <b>to</b>: язык, на который происходит перевод; по умолчанию русский\n"
            "\n"
            "❗ Доступные языки у переводчиков разные, в названии обычно используются"
            " <b>2 латинские буквы</b>, но точные нужно смотреть в самом переводчике.\n"
            "Стандартные, которые есть почти во всех переводчиках: <i>{languages}</i>\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/translate</code>&gt; - переводит текст с помощью Wanson"
            " с распознанного на русский\n"
            "- &lt;<code>/translate lin</code>&gt; - переводит текст с помощью LingvaNex"
            " с распознанного на русский\n"
            "- &lt;<code>/translate uk</code>&gt; - переводит текст с помощью Wanson"
            " с украинского на русский\n"
            "- &lt;<code>/translate en ja</code>&gt; - переводит текст с помощью Wanson"
            " с английского на японский\n"
            "- &lt;<code>/translate lin de fi</code>&gt; - переводит текст с помощью LingvaNex"
            " с немецкого на финский\n"
        ),

        "help": "🐞❓ Произошла рекурсия, не делайте так!",
        "unknown": "🔎 Ищем-ищем... Не нашли справки для &lt;<code>{}</code>&gt;.",
    },
}


# for @BotFather
_bot_info = {
    "user": {
        "commands": (
            "generate - сгенерировать фразу 🅰️\n"
            "chinese - перевод китайских символов 🈲\n"
            "help - справка 🧐\n"
        ),
        "description": (
            "Бот для генерации нейротекста, основанный на странности обучения переводчиков."
        ),
    },
    "admin": {
        "commands": (
            "generate - сгенерировать фразу 🅰️\n"
            "chinese - перевод китайских символов 🈲\n"
            "generate_wat - сгенерировать фразу Waston 🇼️️\n"
            "generate_absurd - сгенерировать абсурдоткекст 🔤\n"
            "lorem - сгенерировать псевдотекст 📃\n"
            "translate - перевод по сообщения 🔄\n"
            "help - справка 🧐\n"
        ),
        "description": (
            "Расширенная версия бота для генерации нейротекста."
        ),
    },
}
