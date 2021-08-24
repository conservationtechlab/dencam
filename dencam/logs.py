import os
import logging
import getpass

from datetime import datetime


def setup_logger(level, filename=None):
    logger = logging.getLogger()
    logger.setLevel(level)

    s_handler = logging.StreamHandler()
    strg = '[%(levelname)s] %(message)s (%(name)s)'
    formatter = logging.Formatter(strg)
    s_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    s_handler.setLevel(logging.DEBUG)

    if not filename:
        now = datetime.now()
        date_time_string = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
        user = getpass.getuser()
        path = os.path.join('/home', user)
        filename = os.path.join(path, date_time_string + '_dencam.log')

    f_handler = logging.FileHandler(filename)

    strg = '%(asctime)s | %(levelname)8s | %(name)18s | %(message)s'
    f_formatter = logging.Formatter(strg,
                                    datefmt='%F %H:%M:%S')
    f_handler.setFormatter(f_formatter)
    logger.addHandler(f_handler)
    f_handler.setLevel(logging.DEBUG)

    return logger
