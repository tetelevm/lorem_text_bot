from dataclasses import dataclass
from typing import List, Callable, Optional

from telegram import (
    Update,
    BotCommand,
    MenuButtonCommands,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import BaseFilter, ChatType, TEXT, UpdateType

from logger import logger
from handlers import (
    FuncType,
    HandlersType,
    Handler,
    received_message,
    command_start_user,
    command_help_user,
    command_generate,
    command_chinese,
    command_start_admin,
    command_help_admin,
    command_generate_wat,
    command_generate_absurd,
    command_lorem,
    command_translate,
)


__all__ = [
    "user_bot_init",
    "admin_bot_init",
    "test_bot_init",
]


@dataclass
class Command:
    """
    All information about the command, collected in one place.
    """

    name: str
    func: HandlersType
    description: Optional[str] = ""
    filters: BaseFilter = BaseFilter()
    to_button: Optional[bool] = False


# command for all bots returning "I don't work with messages"
message_command = Command("_", received_message, filters=ChatType.PRIVATE)


def add_command(
        app: Application,
        handler_decorator: Callable[[HandlersType], FuncType],
        command: Command,
        *,
        as_command: bool = True
):
    """
    Adds a function wrapped in logs and checks from Handler, and sets an
    additional filter on changed messages.
    """

    handler_func = handler_decorator(command.func)
    filters = command.filters & UpdateType.MESSAGE & TEXT
    app.add_handler(
        CommandHandler(command.name, handler_func, filters, block=False)
        if as_command else
        MessageHandler(filters, handler_func, block=False)
    )


async def bot_init(token: str, log_name: str, commands: List[Command]):
    """
    The function that starts the bot. Adds all commands, buttons, menu
    and puts the bot in run mode.
    """

    # bot creation
    app = Application.builder().token(token).build()

    # add all commands
    handler = Handler.get_decorator(log_name)
    for command in commands:
        add_command(app, handler, command)
    add_command(app, handler, message_command, as_command=False)

    # creating a menu of available commands
    bot_commands = [
        BotCommand(command.name, command.description)
        for command in commands
        if command.description
    ]
    await app.bot.set_my_commands(bot_commands)
    await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    # creating buttons under the input field
    # not implemented splitting into rows, so a maximum of 4 buttons is expected
    buttons = [[
        "/" + command.name
        for command in commands
        if command.to_button
    ]]
    handler.buttons = (
        ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        if buttons[0] else
        ReplyKeyboardRemove()
    )

    # bot startup
    await app.initialize()
    await app.updater.start_polling(allowed_updates=[Update.MESSAGE, Update.POLL_ANSWER])
    await app.start()
    logger(f"Bot <{log_name}> has started")
    print(f"Bot <{log_name}> has started")


# =============================================================================


async def user_bot_init(token):
    """
    Function to start a bot for users.
    """
    commands = [
        Command("start", command_start_user, filters=ChatType.PRIVATE),
        Command("generate", command_generate, "сгенерировать фразу 🅰️", to_button=True),
        Command("chinese", command_chinese, "перевод китайских символов 🈲", to_button=True),
        Command("help", command_help_user, "справка 🧐"),
    ]
    await bot_init(token, "user", commands)


async def admin_bot_init(token):
    """
    Function to start a bot for admins.
    """
    commands = [
        Command("start", command_start_admin, filters=ChatType.PRIVATE),
        Command("generate", command_generate, "сгенерировать фразу 🅰️", to_button=True),
        Command("chinese", command_chinese, "перевод китайских символов 🈲", to_button=True),
        Command("generate_wat", command_generate_wat, "сгенерировать фразу Waston 🇼️️", to_button=True),
        Command("generate_absurd", command_generate_absurd, "сгенерировать абсурдоткекст 🔤"),
        Command("lorem", command_lorem, "сгенерировать псевдотекст 📃"),
        Command("translate", command_translate, "перевод по сообщения 🔄"),
        Command("help", command_help_admin, "справка 🧐"),
    ]
    await bot_init(token, "admin", commands)


async def test_bot_init(token):
    """
    Function to start a test bot.
    """
    commands = [
        Command("start", command_start_admin, filters=ChatType.PRIVATE),
        Command("generate", command_generate, "сгенерировать фразу 🅰️", to_button=True),
        Command("chinese", command_chinese, "перевод китайских символов 🈲", to_button=True),
        Command("lorem", command_lorem, "сгенерировать псевдотекст 📃"),
    ]
    await bot_init(token, "test", commands)
