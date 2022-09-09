import re
import random
from typing import List, Tuple

from telegram import Chat
from telegram.error import BadRequest

from envs import envs
from messages import messages
from logger import error_logger
from translator import (
    text_translator,
    TranslationTimeoutException,
    TranslationRequestException,
)


__all__ = [
    "parse_args",
    "translate",
    "channel_utils",
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


class ChannelUtils:
    """
    The class responsible for all work with the channel.
    """

    channel_name = envs["CHANNEL_NAME"]
    last_index = 10  # temporary solution

    async def reply_random_post(self, chat: Chat) -> str:
        """
        Forwards the first post that can be forwarded to the specified
        chat. Can not be forwarded deleted messages or technical
        messages (changed name, avatar).
        """

        miss_count = 20
        for _ in range(miss_count):
            try:
                post_id = random.randint(2, self.last_index)
                await chat.forward_from(self.channel_name, post_id)
                return ""
            except BadRequest as exc:
                # Either the post with this id is deleted
                # or it is technical
                # or the bot is not a channel admin (in this case the
                # error message will return after several tries)
                print(exc)
                pass

        error_logger.error(ConnectionError("The post is not given out"))
        return messages["random"]["error"]

channel_utils = ChannelUtils()
