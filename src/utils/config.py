import configparser
import logging as log
import ast

from src.utils.singleton import singleton
import src.utils.constants as consts
from src.utils.exceptions import ConfigError
from src.utils.tools import os


@singleton
class Config(object):
    def __init__(self, **kwargs):
        self.config_file = kwargs.get('config_file',
                                      os.path.join(consts.PROJECT_DIR, consts.INPUT_DIR, consts.CONFIG_FILE_NAME))
        self.config = self.read_config()
        pass

    def read_config(self):
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            log.info(f"Read config file: {self.config_file}")
            for section in config.sections():
                log.debug(f"Section: {section}")
                for key in config[section]:
                    log.debug(f"{key}: {config.get(section, key)}")
            return config
        except Exception as e:
            log.error(f"Error: {e}")
            raise e

    def get_section(self, section: str):
        try:
            if self.config.has_section(section):
                return self.config[section]
            else:
                log.warning(f"Section: {section} not found in config file")
                return None

        except Exception as e:
            log.error(f"Could not get section: {section}. Error: {e}")
            raise ConfigError

    def get(self, section: str, param: str, default_value=None, return_as_string: bool = True):
        try:
            if self.config.has_option(section, param):
                value = self.config.get(section, param)
                if return_as_string:
                    return value
                else:
                    return ast.literal_eval(value)
            else:
                log.warning(f"Section: {section}, param: {param} not found in config file")
                return default_value

        except Exception as e:
            log.error(f"Could not get {param} from {section}. Error: {e}")
            raise ConfigError

    def get_seeds(self):
        seeds = self.get(section=consts.CRAWLER_SECTION, param=consts.SEEDS_CONFIG_TOKEN, default_value="")
        if not seeds:
            return []

        res = seeds.replace(" ", "").replace("\n", "").split(",")
        return res

    def get_nodes_types(self):
        """
        Get the nodes types from the config file.
        :return: List: [email, ...]
        """
        graph_callbacks = self.get(section=consts.GRAPH_SECTION, param=consts.GRAPH_NODES_CONFIG_TOKEN, default_value="")
        if not graph_callbacks:
            return []

        return graph_callbacks.replace(" ", "").replace("\n", "").split(",")