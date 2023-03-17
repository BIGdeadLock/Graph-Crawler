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
os.makedirs(OUTPUT_DIR_PATH, exist_ok=True)
GRAPH_OUTPUT_FILE_NAME = "graph.pickle"
GRAPH_OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR_PATH, GRAPH_OUTPUT_FILE_NAME)

INPUT_DIR = "input"
INPUT_PATH = os.path.join(PROJECT_DIR, INPUT_DIR)
os.makedirs(INPUT_PATH, exist_ok=True)
CONFIG_FILE_NAME = "config.ini"
CONFIG_PATH = os.path.join(INPUT_PATH, CONFIG_FILE_NAME)

STORE_DIR = "store"
STORE_PATH = os.path.join(PROJECT_DIR, STORE_DIR)
os.makedirs(STORE_PATH, exist_ok=True)

TEMPLATES_DIR = "templates"
TEMPLATES_PATH = os.path.join(PROJECT_DIR, TEMPLATES_DIR)
os.makedirs(TEMPLATES_PATH, exist_ok=True)
GRAPH_TEMPLATE_FILE_NAME = "graph_template.html"
TEMPLATE_FILE_NAME = "template.html"
GRAPH_TEMPLATE_PATH = os.path.join(TEMPLATES_PATH, GRAPH_TEMPLATE_FILE_NAME)
TEMPLATE_PATH = os.path.join(TEMPLATES_PATH, TEMPLATE_FILE_NAME)

SCHEMA_DIR = "schemas"
SCHEMA_DIR_PATH = os.path.join(PROJECT_DIR, SCHEMA_DIR)
os.makedirs(SCHEMA_DIR_PATH, exist_ok=True)

# -----------------
# SYSTEM CONFIG
# -----------------
SYSTEM_SECTION = "SYSTEM"
NUMBER_OF_JOBS_CONFIG_TOKEN = 'number_of_jobs'

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

# -----------------
# CRAWLER CONFIG SECTION
# -----------------
CRAWLER_SECTION = "CRAWLER"
SEEDS_CONFIG_TOKEN = "seeds"
VALID_WEBSITE_SUFFIXES = [".com", ".org", ".net", ".edu", ".gov", ".mil", ".io", ".co", ".uk", ".jp", ".kr", ".uk",
                          ".in", ".de", ".fr", ".it", ".es", ".nl", ".cz", ".pl", ".ru", ".cn", ".ca", ".au", ".br",
                          ".mx",
                          ]
MAX_DEPTH_CONFIG_TOKEN = "max_depth"

# -----------------
# SCRAPER SECTION
# -----------------
SCRAPER_SECTION = "SCRAPER"
EMAIL_SCRAPER_TOKEN = "email"
LINKS_SCRAPER_TOKEN = "links"
SCRAPERS_CONFIG_TOKEN = "scrapers"
DATA_TOKEN = "data"
WEIGHT_TOKEN = 'weight'
SCRAPER_ID_TOKEN = 'scraper_id'

# -----------------
# SCHEMAS FILES
# -----------------
GRAPH_BUILD_SCHEMA_FILE_NAME = "build.yml"
GRAPH_BUILD_SCHEMA_FILE_PATH = os.path.join(SCHEMA_DIR_PATH, GRAPH_BUILD_SCHEMA_FILE_NAME)
TOP_N_SCHEMA_FILE_NAME = "top_n.yml"
TOP_N_SCHEMA_FILE_PATH = os.path.join(SCHEMA_DIR_PATH, TOP_N_SCHEMA_FILE_NAME)
