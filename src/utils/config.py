import inspect
import configparser
import logging as log
import ast

from src.utils.singleton import singleton
import src.utils.constants as consts
from src.utils.exceptions import ConfigError
from src.utils.tools import os

def func_args() -> list:
    caller = inspect.stack()[1][0]
    args, _, _, values = inspect.getargvalues(caller)
    data = [(i, values[i]) for i in args]
    return data[1:]

def get_caller_info(skip: int = 1) -> dict:
    ret = {"model": "N.A.", "func": "N.A.", "line": 0} # , "msg": "N.A."}
    try:
        frame = inspect.stack()[skip]
        ret["model"] = os.path.split(frame[0].f_code.co_filename)[1]
        ret["func"] = frame[0].f_code.co_name
        ret["line"] = frame[0].f_lineno
#        ret["msg"] = f'Called from {ret["model"]}:{ret["func"]}:{ret["line"]}'
    except Exception as _e:
        log.error(f"Error: {_e}")
    return ret

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

    def get_formated(self, formated_param: str, default_value=None, return_as_string: bool = True):
        try:
            data = formated_param.split(".")
            if len(data) != 2:
                msg = get_caller_info(skip=2)
                log.error(f"The given parameter {formated_param} must have exactly one '.' it should be 'section.parameter'")
                log.error(f"\t{msg}")
                return None
            return self.get(section=data[0], param=data[1], default_value=default_value, return_as_string=return_as_string, call_depth=3)
        except Exception as e:
            log.error(f"Error: {e}")
            raise e

    def get(self, section: str, param: str, default_value=None, return_as_string: bool = True, call_depth: int = 1):
        try:
            u_param = param.upper()
            env_var_name = section + '_' + u_param
            if env_var_name in os.environ:
                log.info(f"Use the environment variable for {env_var_name}: {os.environ[u_param]}")
                return os.environ[env_var_name]
            data = self.config.get(section, param).split("#")[0].strip()
            if not return_as_string:
                c_data = self._get_correct_type(data)
                if c_data is not None:
                    data = c_data
            return data
        except Exception as e:
            if default_value is not None:
                log.warning(f"Used default value {default_value} for {section}, {param}, it was not init in {self.config_file}")
                return default_value
            err_msg = get_caller_info(skip=call_depth)
            msg = f"Reading {self.config_file}: Error {e}\n\tCalled from {err_msg}"
            log.error(msg)
            raise ConfigError(
                fargs=func_args(),
                e='Undefined config parameter',
                message=msg
            )

    # for default value "True": return True if the flag is not defined or its value is "True" else False
    # for default value "False": return False if the flag is not defined or its value is "False" else True
    def check_flag(self, section: str, param: str, default_value: bool) -> bool:
        value = str(default_value).lower()
        ret = self.get(section=section, param=param, default_value=value).lower() == "true"
        return ret

    def _get_correct_type(self, v: str):
        val_to_return = None
        try:
            try:
                val_to_return = ast.literal_eval(v)
            except Exception as e:
                corrected = "\'" + v + "\'"
                val_to_return = ast.literal_eval(corrected)
            return val_to_return
        except Exception as e:
            log.error(f"Error checking type! (Exception: {e})")
        return val_to_return