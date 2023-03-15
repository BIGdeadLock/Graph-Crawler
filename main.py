
import threading
import logging as log

import src.utils.constants as consts
from src.utils.tools import os

from src.utils.log import set_logger
from src.utils.config import Config
from src.server.run_server import RunServer
from src.server.server import ServerInterface


def init_server_interface():
    ServerInterface(config=config)


if __name__ == '__main__':
    try:
        set_logger()
        config_file = os.path.join(consts.PROJECT_DIR, consts.INPUT_DIR, consts.CONFIG_FILE_NAME)
        config = Config(config_file=config_file)
        init_server_interface()
        server = RunServer(section=consts.SERVER_SECTION)
        threading.Thread(target=server.run_server).start()

    except Exception as e:
        log.error(f"Exit with Error: {e}")
