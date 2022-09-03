from __future__ import annotations
import re
from functools import wraps
from typing import List, Tuple, Dict, Set, Any, Callable, Coroutine

from telegram import Update, Chat, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from logger import logger, error_logger
from messages import messages
from translator import (
    text_translator,
    TranslationTimeoutException,
    TranslationRequestException,
)


__all__ = [
    "FuncType",
    "HandlersType",
    "Handler",
    "parse_args",
    "translate",
]


FuncType = Coroutine[Any, Any, str]
HandlersType = Callable[[Update, CallbackContext], FuncType]


class Handler:
    """
    A class for all handlers. Instance class must be used as a decorator
    for handler functions.
    The decorator must be created using the `get_decorator` method.
    """

    name: str
    running_tasks: Set[int]
    buttons: ReplyKeyboardMarkup

    _instances: Dict[str, Handler] = {}

    def __init__(self, name: str):
        self.name = name
        self.running_tasks = set()
        self.buttons = ReplyKeyboardMarkup([])

    @classmethod
    def get_decorator(cls, name: str) -> Handler:
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
        logger.info(f"  {self.name} >>| {user_id} : {flat_msg}")

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

