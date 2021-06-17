#!/usr/bin/env python

from dotenv import load_dotenv
from pathlib import Path
import os
import logging


class Logger():
    # Load up the environment variables
    env_file_name = '.env'
    env_path = Path('.') / env_file_name
    load_dotenv(dotenv_path=env_path)

    # Check if .env.local exists, if so, load up those variables, overriding
    # the previously set ones
    local_env_file_name = env_file_name + '.local'
    local_env_path = Path('.') / local_env_file_name
    if os.path.isfile(local_env_file_name):
        load_dotenv(dotenv_path=local_env_path, override=True)

    def __init__(self, name, logger_level=None):
        """
        Set up the logger instance
        """
        self._name = name
        self._logger = logging.getLogger(self._name)

        # Allow for an override, mostly for debugging during development.
        # This way a single cog can be isolated if needed.
        if logger_level:
            self._logger_level = logger_level
        else:
            self._logger_level = os.environ['LOGGER_LEVEL'].lower()

        # Set the logging level
        if self._logger_level == "debug":
            print("Logging level: DEBUG")
            self._logger.setLevel(logging.DEBUG)
        elif self._logger_level == "info":
            print("Logging level: INFO")
            self._logger.setLevel(logging.INFO)
        elif self._logger_level == "warning":
            print("Logging level: WARNING")
            self._logger.setLevel(logging.WARNING)
        elif self._logger_level == "error":
            print("Logging level: ERROR")
            self._logger.setLevel(logging.ERROR)
        elif self._logger_level == "critical":
            print("Logging level: CRITICAL")
            self._logger.setLevel(logging.CRITICAL)
        else:
            print("Logging level: default (ERROR)")
            self._logger.setLevel(logging.ERROR)

        handler = logging.FileHandler(filename=f"log/{self._name}.log", encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self._logger.addHandler(handler)

    def __enter__(self):
        return self

    def debug(self, *args):
        return self._logger.debug(*args)

    def info(self, *args):
        return self._logger.info(*args)

    def warning(self, *args):
        return self._logger.warning(*args)

    def error(self, *args):
        return self._logger.error(*args)

    def critical(self, *args):
        return self._logger.critical(*args)
