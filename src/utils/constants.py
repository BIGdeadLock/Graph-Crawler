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
INPUT_PATH = os.path.join(PROJECT_DIR, INPUT_DIR)
os.makedirs(INPUT_PATH, exist_ok=True)
CONFIG_FILE_NAME = "config.ini"
CONFIG_PATH = os.path.join(INPUT_PATH, CONFIG_FILE_NAME)

STORE_DIR = "store"
STORE_PATH = os.path.join(PROJECT_DIR, STORE_DIR)
os.makedirs(STORE_PATH, exist_ok=True)


# -----------------
# SERVER TOKENS
# -----------------
HTTP_OK = 200
RESP_SERVER_ERROR_VAL = 500
POST_TOKEN = "POST"
GET_TOKEN = "GET"
DEFAULT_URL_PREFIX = "/api/v1"

# -----------------
# SERVER CONFIG SECTION
# -----------------
SERVER_SECTION = "SERVER"
CONFIG_PORT_TOKEN = "port"
CONFIG_HOST_TOKEN = "host"
CONFIG_IP_TOKEN = "ip"
CONFIG_URL_PREFIX_TOKEN = "url_prefix"
