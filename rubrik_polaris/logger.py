import logging
from logging.handlers import RotatingFileHandler

MAXIMUM_FILE_SIZE = 10000000
BACKUP_COUNT = 3


def logging_setup(logging_level=logging.WARNING) -> logging.Logger:
    """ Init logger object for logging in rubrik-sdk
        For more info - https://docs.python.org/3/library/logging.html
    Args:
        logging_level(int): Log level

    Returns:
        logging.Logger: logger object
    """
    logger = logging.getLogger('rubrik-sdk')

    logger.setLevel(logging_level)

    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(filename)s - line %(lineno)d --> %(message)s')

    file_handler = RotatingFileHandler("rubrik_polaris.log", maxBytes=MAXIMUM_FILE_SIZE, backupCount=BACKUP_COUNT)

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
