

import logging as log
from datetime import datetime
import os
import sys

import src.utils.constants as consts
from logging.handlers import RotatingFileHandler

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_SCREEN_FORMAT = '%(asctime)s [%(module)s:%(funcName)s] [%(lineno)s] [%(levelname)s] %(message)s'
LOG_FILE_FORMAT = '%(asctime)s [%(module)s:%(funcName)s] [%(lineno)s] [%(threadName)s] [%(levelname)s] %(message)s'

LOG_DIR_PATH = os.path.join(consts.STORE_PATH, "log")
os.makedirs(LOG_DIR_PATH, exist_ok=True)

TIMESTAMP = datetime.now().strftime('%Y.%m.%d_%H.%M.%S')

LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, "system.log")

if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)


def set_logger():
    if not os.path.exists(LOG_DIR_PATH):
        os.makedirs(LOG_DIR_PATH)

    console_log_format = log.Formatter(LOG_SCREEN_FORMAT, TIME_FORMAT)
    file_log_format = log.Formatter(LOG_FILE_FORMAT, TIME_FORMAT)

    # Console Handler
    console_handler = log.StreamHandler(sys.stdout)
    console_handler.setLevel(log.INFO)
    console_handler.setFormatter(console_log_format)

    # File Handler
    # Set the log file size to 1GB
    file_handler = RotatingFileHandler(LOG_FILE_PATH, mode='w', maxBytes=1000 * 1024 * 1024, backupCount=1)
    file_handler.setLevel(log.INFO)
    file_handler.setFormatter(file_log_format)

    # Set Logger
    log.basicConfig(datefmt=TIME_FORMAT,
                    level=log.INFO,
                    handlers=[
                        console_handler,
                        file_handler
                    ])
