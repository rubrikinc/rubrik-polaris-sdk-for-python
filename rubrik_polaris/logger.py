import logging

MAXIMUM_FILE_SIZE = 10000000
BACKUP_COUNT = 3


def logging_setup(logging_handler, logging_level) -> logging.Logger:
    """ Init logger object for logging in rubrik-sdk
        For more info - https://docs.python.org/3/library/logging.html
    Args:
        logging_level(int): Log level
        logging_handler (Handler): Handler to log

    Returns:
        logging.Logger: logger object
    """
    logger = logging.getLogger('rubrik-sdk')

    logger.setLevel(logging_level)

    logger.addHandler(logging_handler)

    return logger
