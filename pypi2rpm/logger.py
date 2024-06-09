from colorlog import getLogger, StreamHandler, ColoredFormatter
from logging import Logger


def get_logger(app_name: str) -> Logger:
    handler = StreamHandler()
    handler.setFormatter(
        ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s")
    )

    logger = getLogger(app_name)
    logger.addHandler(handler)
    return logger
