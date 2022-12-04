from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Type

from telegram import (
    Update,
    BotCommand,
    MenuButtonCommands,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    BaseHandler,
    CommandHandler,
    MessageHandler,
)
from telegram.ext.filters import BaseFilter, ChatType, Text, TEXT

from logger import logger
from handlers import (
    HandlersType,
    HandlerDecorator,

    # echo,
    received_message,
    command_start_user,
    command_help_user,
    command_generate,
    command_chinese,
    command_random,
    new_channel_post,
    command_start_admin,
    command_help_admin,
    command_generate_wat,
    command_generate_absurd,
    command_lorem,
    command_lorem_tt,
    command_translate,
    repeat_command,
)


__all__ = [
    "user_bot_init",
    "admin_bot_init",
    "test_bot_init",
]


@dataclass
class Handler(ABC):
    """
    A class for storage of handler parameters.
    """

    func: HandlersType
    name: str = ""
    filters: BaseFilter = BaseFilter()
    command_type: Type[BaseHandler] = BaseHandler
    description: Optional[str] = ""
    to_button: Optional[bool] = False
    _with_decorator: bool = True

    @abstractmethod
    def get_args(self, decorator: HandlerDecorator) -> tuple:
        """
        Returns the parameters required for initializing `self.command_type`.
        """
        pass


@dataclass
class Command(Handler):
    command_type: Type[BaseHandler] = CommandHandler

    def get_args(self, decorator: HandlerDecorator) -> tuple:
        return (self.name, decorator(self.func), self.filters, False)


@dataclass
class Message(Handler):
    command_type: Type[BaseHandler] = MessageHandler

    def get_args(self, decorator: HandlerDecorator) -> tuple:
        func = decorator(self.func) if self._with_decorator else self.func
        return (self.filters, func, False)


# =============================================================================


async def bot_init(token: str, log_name: str, handlers: List[Handler]):
    """
    The function that starts the bot. Adds all commands, buttons, menu
    and puts the bot in run mode.
    """

    # bot creation
    app = Application.builder().token(token).build()

    # add all commands
    handler_decorator = HandlerDecorator.get_decorator(log_name, app)
    for handler in handlers:
        handler_obj = handler.command_type(*handler.get_args(handler_decorator))
        app.add_handler(handler_obj)

    # creating a menu of available commands
    bot_commands = [
        BotCommand(command.name, command.description)
        for command in handlers  # only for commands
        if command.description
    ]
    await app.bot.set_my_commands(bot_commands)
    await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    # creating buttons under the input field; 0-6 buttons is expected
    buttons = [[
        "/" + command.name
        for command in handlers  # only for commands
        if command.to_button
    ]]
    if len(buttons[0]) > 3:
        count_top = 2 if len(buttons[0]) == 4 else 3
        buttons = [buttons[0][:count_top], buttons[0][count_top:]]
    handler_decorator.buttons = (
        ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
        if buttons[0] else
        ReplyKeyboardRemove()
    )

    # bot startup
    allowed_updates = [Update.MESSAGE, Update.CHANNEL_POST, Update.POLL_ANSWER]
    await app.initialize()
    await app.updater.start_polling(allowed_updates=allowed_updates)
    await app.start()
    logger(f"Bot <{log_name}> has started")
    print(f"Bot <{log_name}> has started")


# =============================================================================


async def user_bot_init(token):
    """
    Function to start a bot for users.
    """
    commands = [
        Command(command_start_user, "start", TEXT & ChatType.PRIVATE),
        Command(command_generate, "generate", TEXT, description="сгенерировать фразу 🅰️", to_button=True),
        Command(command_chinese, "chinese", TEXT, description="перевод китайских символов 🈲", to_button=True),
        Command(command_random, "random", TEXT, description="случайный пост из канала 📓", to_button=True),
        Command(command_help_user, "help", TEXT, description="справка 🧐"),
        Message(received_message, filters=TEXT & ChatType.PRIVATE),
        Message(new_channel_post, filters=TEXT & ChatType.CHANNEL, _with_decorator=False),
    ]
    await bot_init(token, "user", commands)


async def admin_bot_init(token):
    """
    Function to start a bot for admins.
    """
    commands = [
        Command(command_start_admin, "start", TEXT & ChatType.PRIVATE),
        Command(command_lorem_tt, "lorem_tt", TEXT, description="сгенерировать псевдотатарское 📃", to_button=True),
        Command(command_generate, "generate", TEXT, description="сгенерировать фразу 🅰️"),
        Command(command_chinese, "chinese", TEXT, description="перевод китайских символов 🈲", to_button=True),
        Command(command_generate_wat, "generate_wat", TEXT, description="сгенерировать фразу Waston 🇼️️", to_button=True),
        Command(command_generate_absurd, "generate_absurd", TEXT, description="сгенерировать абсурдоткекст 🔤"),
        Command(command_lorem, "lorem", TEXT, description="сгенерировать псевдотекст 📃", to_button=True),
        Command(command_translate, "translate", TEXT, description="перевод по сообщения 🔄"),
        Command(command_help_admin, "help", TEXT, description="справка 🧐"),
        Message(repeat_command, filters=Text(["+"])),
        Message(received_message, filters=TEXT & ChatType.PRIVATE),
    ]
    await bot_init(token, "admin", commands)


async def test_bot_init(token):
    """
    Function to start a test bot.
    """
    commands = [
        Command(command_start_admin, "start", TEXT & ChatType.PRIVATE),
        Command(command_lorem_tt, "lorem_tt", TEXT, description="сгенерировать псевдотатарское 📃", to_button=True),
        Command(command_generate, "generate", TEXT, description="сгенерировать фразу 🅰️"),
        Command(command_chinese, "chinese", TEXT, description="перевод китайских символов 🈲", to_button=True),
        Command(command_generate_wat, "generate_wat", TEXT, description="сгенерировать фразу Waston 🇼️️", to_button=True),
        Command(command_random, "random", TEXT, description="случайный пост из канала 📓", to_button=True),
        Command(command_lorem, "lorem", TEXT, description="сгенерировать псевдотекст 📃"),
        Command(command_help_admin, "help", TEXT, description="справка 🧐"),
        Message(repeat_command, filters=Text(["+"])),
        Message(received_message, filters=TEXT & ChatType.PRIVATE),
        Message(new_channel_post, filters=TEXT & ChatType.CHANNEL, _with_decorator=False),
    ]
    await bot_init(token, "test", commands)
