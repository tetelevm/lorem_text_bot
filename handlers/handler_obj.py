from __future__ import annotations
from functools import wraps
from typing import Dict, Set, Any, Callable, Coroutine

from telegram import Update, Chat, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from logger import logger, error_logger
from messages import messages

__all__ = [
    "FuncType",
    "HandlersType",
    "HandlerDecorator",
]

FuncType = Coroutine[Any, Any, str]
HandlersType = Callable[[Update, CallbackContext], FuncType]


class HandlerDecorator:
    """
    A class for all handlers. Instance class must be used as a decorator
    for handler functions.
    The decorator must be created using the `get_decorator` method.
    """

    name: str
    running_tasks: Set[int]
    buttons: ReplyKeyboardMarkup

    _instances: Dict[str, HandlerDecorator] = {}

    def __init__(self, name: str):
        self.name = name
        self.running_tasks = set()
        self.buttons = ReplyKeyboardMarkup([])

    @classmethod
    def get_decorator(cls, name: str) -> HandlerDecorator:
        """
        Creates a new decorator with a given name or returns an existing
        one.
        """

        name = name.ljust(6)
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]

    def log_request(self, user_id: int, text: str):
        """
        Logs all requests that come to the bot.
        """

        flat_msg = logger.flatten_string(text)
        msg = f"  {self.name} >>| {user_id} : {flat_msg}"
        print(msg)
        logger.info(msg)

    async def send_message(self, chat: Chat, message: str):
        """
        Sending a message to a user.
        Not the best architectural solution, done because keyboard
        buttons are stored in the handler object.
        """
        await chat.send_message(
            message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=self.buttons
        )

    async def execute(self, coro: FuncType, user_key: int) -> str:
        """
        Checks if there are tasks already running for this user, and if
        not, sets the execution flag and executes the handler.
        Flags of different bots are not shared. That is, if a request is
        executed on a user bot, the second request to it will not be
        executed, but the request to the admin bot can be executed.
        """

        if user_key in self.running_tasks:
            coro.close()
            return messages["already_run"]

        self.running_tasks.add(user_key)
        try:
            return (await coro)
        except Exception as exc:
            error_logger.error(error_logger.get_full_exc_info(exc))
            logger.error(logger.get_exc_info(exc))
            return messages["error"]
        finally:
            self.running_tasks.remove(user_key)

    def __call__(self, func: HandlersType):
        """
        Decorator for handlers. Logs requests, makes checks and catches
        errors. When crashes, it writes logs to a special file and
        outputs a standard error message.
        """

        @wraps(func)
        async def wrapper(update: Update, context: CallbackContext):
            user_id = update.message.from_user.id
            self.log_request(user_id, update.message.text)
            coro = func(update, context)
            message = await self.execute(coro, user_id)
            if message:
                await self.send_message(update.effective_chat, message)

        return wrapper

