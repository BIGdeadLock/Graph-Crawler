import os
import sys


WINDOWS_OS_STR = "nt"
IS_WINDOWS_OS = (os.name == WINDOWS_OS_STR)

PROJECT_DIR = os.environ['PROJECT_DIR'] if 'PROJECT_DIR' in os.environ else os.path.dirname(
    sys.modules['__main__'].__file__)

# -----------------
# FILE PATHS
# -----------------
OUTPUT_DIR = 'output'
OUTPUT_DIR_PATH = os.path.join(PROJECT_DIR, OUTPUT_DIR)

INPUT_DIR = "input"
CONFIG_FILE_NAME = "config.ini"
CONFIG_PATH = os.path.join(PROJECT_DIR, INPUT_DIR, CONFIG_FILE_NAME)