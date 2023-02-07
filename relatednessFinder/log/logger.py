import functools
import logging
import os
from typing import Any

import typer

level_dict: dict[str, int] = {
    "verbose": logging.INFO,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
}


def record_inputs(logger, **kwargs) -> None:
    """function to record the user arguments that were passed to the
    program. Takes a logger and then a dictionary of the user
    arguments"""

    logger.setLevel(20)

    for parameter, value in kwargs.items():
        logger.info(f"{parameter}: {value}")

    # getting the correct log level to reset the logger
    logger.setLevel(get_loglevel(kwargs["loglevel"]))


def get_loglevel(loglevel: str) -> int:
    """Function that will return a log level based on the input"""

    return level_dict[loglevel]


def configure(
    logger: logging.Logger,
    output: str,
    filename: str = "IBDCluster.log",
    loglevel: str = "warning",
    to_console: bool = False,
    format_str: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> None:
    """Function that will configure the level of logging"""

    filename = os.path.join(output, filename)

    logger.setLevel(level_dict.get(loglevel, logging.WARNING))

    file_formatter = logging.Formatter(format_str)

    # program defaults to log to a file called IBDCluster.log in the
    # output directory
    fh = logging.FileHandler(filename, mode="w")
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)

    # If the user selects to also log to console then the program will
    # log information to the stderr
    if to_console:
        stream_formatter = logging.Formatter("%(message)s")

        sh = logging.StreamHandler()
        sh.setFormatter(stream_formatter)
        logger.addHandler(sh)


def get_logger(module_name: str, main_name: str = "__main__") -> logging.Logger:
    """Function that will be responsible for getting the logger for modules"""
    return logging.getLogger(main_name).getChild(module_name)


def create_logger(
    logger_name: str = "__main__",
) -> logging.Logger:
    """function that will get the correct logger for the program

    Parameters

    loglevel : str
        logging level that the user wants to use. The default level is INFO

    Returns

    logging.Logger
    """

    logger = logging.getLogger(logger_name)

    return logger

def log_msg_debug(log_message: str = None):
    def log_decorator(func):
        @functools.wraps(func)
        def log_to_file(*args, **kwargs) -> Any:
            logger = kwargs["logger"]
            logger.debug(log_message)
            if logging.getLevelName(logger.level) == "DEBUG":
                args_repr = [repr(a) for a in args]                      
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  
                signature = ", ".join(args_repr + kwargs_repr)           
                logger.debug(f"calling the function {func.__name__} with the arguments: {signature}")
            try:
                return_val = func(*args, **kwargs)
            except Exception as e:
                logger.critical(e)
                logger.critical(f"Encountered an exception while running the function: {func.__name__}")
                typer.abort()
            return return_val
        return log_to_file
    return log_decorator
