import logging
from types import TracebackType


__all__ = [
    "get_logger",
    "logger",
    "error_logger",
]


def get_traceback(trb: TracebackType) -> list[str]:
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
    def get_exc_info(exc: Exception) -> str:
        """
        Simple transformation of error into single line text.
        """
        return str(exc).replace("\n", " \\n ")

    @staticmethod
    def get_full_exc_info(exc: Exception) -> str:
        """
        Parses the error traceback and formats it for multiline output.
        """

        traceback_crumb = get_traceback(exc.__traceback__)
        max_len = len(max(traceback_crumb, key=len))
        formatted_crumbs = (line.ljust(max_len, " ") for line in traceback_crumb)
        return "\n" + " >\n".join(formatted_crumbs) + " !"


DEFAULT_FORMAT = "{levelname:<8} > {asctime:<23} > {name:<16} > {msg}"

existing_loggers: dict[str, Logger] = {}


def get_logger(
        name: str = "logger",
        file: str = "logs/log.txt",
        fmt: str = DEFAULT_FORMAT,
        level: (int | str) = logging.WARNING,
) -> Logger:
    """
    Custom logger initialization.
    """

    if len(name) > 16:
        raise Exception(f'Name "{name}" is very long (maximum 16 symbols)')

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
