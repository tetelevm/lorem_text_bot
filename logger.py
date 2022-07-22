import logging
from typing import List, Dict, Union
from types import TracebackType


__all__ = [
    "get_logger",
    "logger",
    "error_logger",
]


def get_traceback(trb: TracebackType) -> List[str]:
    """
    Collects the file and string of the current frame and recursively
    adds the next to it.
    """

    frame = f"{trb.tb_frame.f_code.co_filename} :{trb.tb_frame.f_lineno}"
    if trb.tb_next is None:
        return [frame]
    return [frame] + get_traceback(trb.tb_next)


class Logger(logging.Logger):
    """
    A class that adds error formatting methods to the standard logger.
    """

    def __call__(self, msg):
        self.info(msg)

    @staticmethod
    def flatten_string(string: str) -> str:
        """
        Translates multiline text to a single line.
        """
        return str(string).replace("\n", " \\n ")

    @classmethod
    def get_exc_info(cls, exc: Exception) -> str:
        """
        Simple transformation of error into single line text.
        """
        return cls.flatten_string(str(exc))

    @classmethod
    def get_full_exc_info(cls, exc: Exception) -> str:
        """
        Parses the error traceback and formats it for multiline output.
        """

        traceback_crumb = get_traceback(exc.__traceback__)
        max_len = len(max(traceback_crumb, key=len))
        formatted_crumbs = (line.ljust(max_len, " ") for line in traceback_crumb)
        crumbs = " >\n".join(formatted_crumbs) + " !"
        exc_str = cls.get_exc_info(exc)
        return f"\n{crumbs}\n{exc_str}"


DEFAULT_FORMAT = "{levelname:<8} > {asctime:<23} >>| {msg}"

existing_loggers: Dict[str, Logger] = {}


def get_logger(
        name: str = "logger",
        file: str = "logs/log.txt",
        fmt: str = DEFAULT_FORMAT,
        level: Union[int, str] = logging.WARNING,
) -> Logger:
    """
    Custom logger initialization.
    """

    if name not in existing_loggers:
        logger_ = Logger(name, level)
        handler = logging.FileHandler(file, mode='a')
        formatter = logging.Formatter(fmt, style='{')
        handler.setFormatter(formatter)
        logger_.addHandler(handler)
        existing_loggers[name] = logger_

    return existing_loggers[name]


logger = get_logger(level="INFO")
error_logger = get_logger("error", "logs/error.txt", DEFAULT_FORMAT + "\n")
