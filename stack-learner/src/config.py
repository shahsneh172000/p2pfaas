#  P2PFaaS - A framework for FaaS Load Balancing
#  Copyright (c) 2019 - 2022. Gabriele Proietti Mattia <pm.gabriele@outlook.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os

# ENV_LEARNER = "P2PFAAS_LEARNER"
# ENV_APPROXIMATOR = "P2PFAAS_APPROXIMATOR"
# ENV_TD_FORM = "P2PFAAS_TD_FORM"
# ENV_ACTIONS_NUM = "P2PFAAS_ACTIONS_NUM"
# ENV_PARAMETERS = "P2PFAAS_PARAMETERS"
import log

_ENV_LISTENING_HOST = "P2PFAAS_LISTENING_HOST"
_ENV_LISTENING_PORT = "P2PFAAS_LISTENING_PORT"
_ENV_DIR_DATA = "P2PFAAS_DIR_DATA"
_ENV_RUNNING_ENVIRONMENT = "P2PFAAS_RUNNING_ENVIRONMENT"


class ConfigurationStatic:
    _instance = None

    _DEFAULT_RUNNING_ENVIRONMENT = "production"
    _DEFAULT_DIR_DATA = "/data"
    _DEFAULT_LISTENING_HOST = "0.0.0.0"
    _DEFAULT_LISTENING_PORT = 19020

    @classmethod
    def _init(cls):
        cls._running_environment = os.getenv(_ENV_RUNNING_ENVIRONMENT, default=ConfigurationStatic._DEFAULT_RUNNING_ENVIRONMENT)
        cls._dir_data = os.getenv(_ENV_DIR_DATA, default=ConfigurationStatic._DEFAULT_DIR_DATA)
        cls._listening_host = os.getenv(_ENV_LISTENING_HOST, default=ConfigurationStatic._DEFAULT_LISTENING_HOST)
        cls._listening_port = os.getenv(_ENV_LISTENING_PORT, default=ConfigurationStatic._DEFAULT_LISTENING_PORT)

        cls._listening_port = int(cls._listening_port)
        cls._is_development = cls._running_environment == "development"

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._init()
        return cls._instance

    #
    # Exported
    #

    def get_dir_data(self):
        return self._dir_data

    def is_development(self):
        return self._is_development

    def get_listening_host(self) -> str:
        return self._listening_host

    def get_listening_port(self) -> int:
        return self._listening_port

    @staticmethod
    def get_app_name():
        return "p2pfaas-learner"

    @staticmethod
    def get_app_version():
        return "0.0.1b"


class ConfigurationDynamic:
    _MODULE_NAME = "ConfigurationDynamic"
    _instance = None

    _DICT_LEARNER_NAME_KEY = "learner_name"
    _DICT_LEARNER_PARAMETERS_KEY = "learner_parameters"

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def _init(cls):
        # base vars
        cls._learner_name = ""  # the configuration dict
        cls._learner_parameters = {}  # the configuration dict

        # try to read from file
        cls._file_read(ConfigurationDynamic._instance)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._init()
        return cls._instance

    def set_learner_name(self, name):
        # noinspection PyAttributeOutsideInit
        self._learner_name = name
        self._file_save()

    def set_learner_parameters(self, parameters: dict):
        # noinspection PyAttributeOutsideInit
        self._learner_parameters = parameters
        self._file_save()

    def get_learner_name(self):
        # noinspection PyAttributeOutsideInit
        return self._learner_name

    def get_learner_parameters(self):
        # noinspection PyAttributeOutsideInit
        return self._learner_parameters

    def _file_save(self):
        """Save configuration to file"""
        try:
            os.makedirs(ConfigurationStatic.instance().get_dir_data(), exist_ok=True)

            conf_dict = self._to_dict()

            conf_str = json.dumps(conf_dict, indent=2)
            conf_file = open(self._file_path(), "w")
            conf_file.write(conf_str)
            conf_file.close()

        except Exception as e:
            self._dict = {}
            log.Log.mwarn(ConfigurationDynamic._MODULE_NAME,
                          f"_file_save: Could not write the config file at {self._file_path()}: {e}")

    def _file_read(self):
        """Read configuration from file"""
        try:
            config_file = open(self._file_path(), "r")
            config_str = ""
            for line in config_file:
                config_str += line
            config_file.close()

            conf_dict = json.loads(config_str)

            if conf_dict is None:
                raise FileNotFoundError()

            if ConfigurationDynamic._DICT_LEARNER_NAME_KEY in conf_dict.keys():
                self._learner_name = conf_dict[ConfigurationDynamic._DICT_LEARNER_NAME_KEY]

            if ConfigurationDynamic._DICT_LEARNER_PARAMETERS_KEY in conf_dict.keys():
                self._learner_parameters = conf_dict[ConfigurationDynamic._DICT_LEARNER_PARAMETERS_KEY]

            log.Log.minfo(ConfigurationDynamic._MODULE_NAME, f"_file_read: read configuration from file {self._file_path()}")

        except Exception as e:
            self._dict = {}
            log.Log.mwarn(ConfigurationDynamic._MODULE_NAME,
                          f"_file_read: Could not read the config file at {self._file_path()}: {e}")

    def _file_path(self):
        return f"{ConfigurationStatic.instance().get_dir_data()}/p2pfaas_learner.json"

    def _to_dict(self):
        return {
            ConfigurationDynamic._DICT_LEARNER_NAME_KEY: self._learner_name,
            ConfigurationDynamic._DICT_LEARNER_PARAMETERS_KEY: self._learner_parameters
        }
