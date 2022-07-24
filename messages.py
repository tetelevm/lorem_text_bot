__all__ = [
    "messages",
]

messages = {
    "error": "🪲 500 🪲 На сервере произошла какая-то ошибка, уже чиним!",

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
    "start": (
        "🖐 Привет! Вот мои команды:\n"
        "📃 /lorem - сгенерировать <b>псевдотекст</b>\n"
        "🈲 /translate - <b>перевод</b> текста по реплаю сообщения\n"
        "🧐 /help - <b>справка</b> (более подробно и со ссылкой на документацию)"
    ),

    "help": {
        "help": "🐞❓ Произошла рекурсия, не делайте так!",
        "default": (
            "❓ Я - бот для генерации псевдотекстов 🤖. Я знаю команды:\n"
            "\n"
            "📃 /lorem - по определённому алгоритму создаю <b>текст с бессмысленными словами</b>,"
            " который по звучанию похож на русский, но по факту лорем\n"
            "\n"
            "🈲 /translate - работаю по реплаю на сообщения: <b>беру его текст</b> и отправляю"
            " одному из переводчиков на перевод\n"
            "\n"
            "🧐 /help - выводит это сообщение\n"
            "\n"
            "🤓 Вызови &lt;<code>/help [команда]</code>&gt;, если хочешь подробное описание:\n"
            "<code>/help /lorem</code>\n"
            "<code>/help /translate</code>\n"
            "\n"
            "Исходники и собранная воедино справка"
            " &lt;<a href=\"https://github.com/tetelevm/lorem_text_bot\">лежат тут</a>&gt; 🐙."
            " Там же можно спросить вопросов."
        ),
        "unknown": "🔎 Ищем-ищем... Не нашли справки для &lt;<code>{}</code>&gt;.",
    },

    "lorem": {
        "help": (
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
            "- <b>количество сгенерированных слов</b>: по умолчанию 48, варианты 32-256\n"
            "- <b>длина буфера</b>: по умолчанию 2, варианты 1-3\n"
            "\n"
            "📗 Примеры:\n"
            "- &lt;<code>/lorem</code>&gt; - стандартная генерация 48 слов на русском\n"
            "- &lt;<code>/lorem 128</code>&gt; - генерация 128 слов\n"
            "- &lt;<code>/lorem 64 1</code>&gt; - генерация 64 слов с буфером 1\n"
            "- &lt;<code>/lorem el 32</code>&gt; - генерация 32 слов на греческом\n"
            "- &lt;<code>/lorem en 48 3</code>&gt; - генерация 48 слов на английском с буфером 3\n"
        ),
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
        "help": (
            "🈲 <code>/translate</code> переводит текст с помощью переводчика с одного"
            " языка на другой\n"
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
            "Стандартные, которые есть почти во всех переводчиках: <i>en, ru, el, de, ja</i>\n"
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
        "no_reply": "🐞 Переводы работают только с ответами сообщений.",
        "no_reply_text": "🐞 В сообщении из ответа нет текста, не могу перевести.",
        "translator_error": (
            "🐞 Неизвестный переводчик &lt;<code>{}</code>&gt;. Переводчикии, которыми я умею"
            " переводить, вы можете посмотреть командой &lt;<code>/help /lorem</code>&gt;."
        ),
        "timeout_error": (
            "🐞 Сервер слишком долго не отвечает, запрос перевода оборван. Скорее всего, сервер"
            " просто завис при запросе или заснул при переводе. Попробуйте повторить."
        ),
        "request_error": (
            "🐞 Ошибка в запросе. Возможно, неизвестный серверу язык или какая-то другая"
            " непонятная причина."
        ),
    },

    "todo": "💻 Функционал ещё не готов, пытаемся реализовать.",
}
