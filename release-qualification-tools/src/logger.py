import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

LOG_LEVELS = {"INFO": logging.INFO, "ERROR": logging.ERROR}


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(FORMATTER)
    logger.addHandler(sh)
    return logger
