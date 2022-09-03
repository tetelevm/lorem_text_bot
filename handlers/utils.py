import re
import random
from typing import List, Tuple

from telegram import Chat
from telegram.error import BadRequest

from envs import envs
from messages import messages
from translator import (
    text_translator,
    TranslationTimeoutException,
    TranslationRequestException,
)


__all__ = [
    "parse_args",
    "translate",
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

