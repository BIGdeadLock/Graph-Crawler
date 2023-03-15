# IBM Confidential - OCO Source Materials
# (C) Copyright IBM Corp. 2020
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.

__author__ = "IBM"

import logging as log
from datetime import datetime
import os
import sys

import src.utils.definition as consts
from logging.handlers import SocketHandler, RotatingFileHandler

DEBUG = True

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_SCREEN_FORMAT = '%(asctime)s [%(module)s:%(funcName)s] [%(lineno)s] [%(levelname)s] %(message)s'
# LOG_SCREEN_FORMAT = '%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s'
LOG_FILE_FORMAT = '%(asctime)s [%(module)s:%(funcName)s] [%(lineno)s] [%(threadName)s] [%(levelname)s] %(message)s'
if not DEBUG:
    LOG_DIR_PATH = os.path.join(consts.PROJECT_DIR, "store", "log", (datetime.now()).strftime('%Y-%m-%d_%H-%M'))
else:
    LOG_DIR_PATH = os.path.join(consts.PROJECT_DIR, "store", "log")
TIMESTAMP = datetime.now().strftime('%Y.%m.%d_%H.%M.%S')
if not DEBUG:
    LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, f"orchestrator_{TIMESTAMP}.log")
else:
    LOG_FILE_PATH = os.path.join(LOG_DIR_PATH, f"orchestrator.log")

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

#
# # TODO: Delete after demo
# demo_logger = log.getLogger("demo")
# log_path = os.path.join(consts.PROJECT_DIR, 'store', 'log', "demo.log")
# format = '%(asctime)s %(message)s'
# file_log_format = log.Formatter(format, TIME_FORMAT)
#
# file_handler = log.FileHandler(filename=LOG_FILE_PATH)
# file_handler.setLevel(log.INFO)
# file_handler.setFormatter(file_log_format)
#
# console_handler = log.StreamHandler(sys.stdout)
#
# socket_handler = log.handlers.SocketHandler('9.148.28.238', 5000)
#
# demo_logger.addHandler(file_handler)
# demo_logger.addHandler(console_handler)
# demo_logger.addHandler(socket_handler)
#
# backup_demo_logger = log.getLogger("backup_demo")
# socket_handler = log.handlers.SocketHandler('9.148.28.238', 5003)
# backup_demo_logger.addHandler(socket_handler)
#
# def on_backup_demo_logger():
#     logger = log.getLogger("demo")
#     socket_handler = log.handlers.SocketHandler('9.148.28.238', 5003)
#     logger.addHandler(socket_handler)
#
# def off_backup_demo_logger():
#     logger = log.getLogger("demo")
#     socket_handler = log.handlers.SocketHandler('9.148.28.238', 5000)
#     logger.addHandler(socket_handler)
#
