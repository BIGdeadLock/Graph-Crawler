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
GRAPH_OUTPUT_FILE_NAME = "graph.pkl"
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
TIMEOUT_CONFIG_TOKEN = "timeout"
MAX_RETIRES_CONFIG_TOKEN = "max_retries"
MAX_REQUEST_CONFIG_TOKEN = "max_requests"

IGNORED_EXTENSIONS = [
    # archives
    '7z', '7zip', 'bz2', 'rar', 'tar', 'tar.gz', 'xz', 'zip',
    # images
    'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif', 'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps',
    'svg', 'cdr', 'ico',
    # audio
    'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',
    # video
    '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv', 'm4a', 'm4v', 'flv', 'webm',
    # office suites
    'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg', 'odp',
    # other
    'css', 'pdf', 'exe', 'bin', 'rss', 'dmg', 'iso', 'apk', 'jar', 'csv', 'js', 'json', 'xml', 'swf', 'class', 'psd'
]

# -----------------
# GRAPH SECTION
GRAPH_SECTION = "GRAPH"
EMAIL_TYPE_TOKEN = "email"
URL_TYPE_TOKEN = "url"
GRAPH_CALLBACKS_TOKEN = "graph"
REQUEST_NODES_TOKEN = "nodes"
DATA_TOKEN = "data"
WEIGHT_TOKEN = 'weight'
CALLBACK_ID_TOKEN = 'callback_id'
GRAPH_NODES_CONFIG_TOKEN = "nodes"
ALPHA_CONFIG_TOKEN = "alpha"

# -----------------
# FILTERS SECTION
# -----------------
FILTERS_SECTION = "FILTERS"
DOMAIN_FILTER = "domain"
SUBDOMAIN_FILTER = "subdomain"
PATTERN_RULES = "pattern_rules"

# -----------------
# SCHEMAS FILES
# -----------------
GRAPH_BUILD_SCHEMA_FILE_NAME = "build.yml"
GRAPH_BUILD_SCHEMA_FILE_PATH = os.path.join(SCHEMA_DIR_PATH, GRAPH_BUILD_SCHEMA_FILE_NAME)
TOP_N_SCHEMA_FILE_NAME = "top_n.yml"
TOP_N_SCHEMA_FILE_PATH = os.path.join(SCHEMA_DIR_PATH, TOP_N_SCHEMA_FILE_NAME)
