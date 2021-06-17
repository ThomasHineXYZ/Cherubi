#!/usr/bin/env python

from dotenv import load_dotenv
from lib.mysql import mysql
from pathlib import Path
from pythonjsonlogger import jsonlogger
import os
import logging
import sys


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

        # Set the handler and the level
        self._set_level(logger_level)
        handler = self._set_handler()

        if os.environ['DEBUG'].lower() == "true":
            print(f"Logger set to {self._logger_level.upper()} and {self._logger_stream.upper()}")

        # Finally, add in the configured handler
        self._logger.addHandler(handler)

    def _set_handler(self):
        # Set where the logger gets stored
        self._logger_stream = os.environ['LOGGER_STREAM'].lower()

        if self._logger_stream == "file":
            handler = logging.FileHandler(filename=f"log/{self._name}.log", encoding='utf-8', mode='w')
            handler.setFormatter(logging.Formatter(
                "%(asctime)s:%(levelname)s:%(name)s: %(message)s",
                "%Y-%m-%d %H:%M:%S"
            ))

        elif (
            (self._logger_stream == "stdout")
            or (self._logger_stream == "terminal")
        ):
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setFormatter(logging.Formatter(
                "%(levelname)s:%(name)s: %(message)s",
                "%Y-%m-%d %H:%M:%S"
            ))

        elif self._logger_stream == "json":
            handler = logging.FileHandler(filename=f"log/{self._name}.json", encoding='utf-8', mode='w')
            formatter = jsonlogger.JsonFormatter()
            handler.setFormatter(formatter)

        elif self._logger_stream == "mysql":
            # The split character is changed to §, since I doubt this will come
            # up in any logger stuff
            handler = logging.StreamHandler(MySQLStreamHandler())
            handler.setFormatter(logging.Formatter(
                "%(asctime)s§%(levelname)s§%(name)s§%(message)s",
                "%Y-%m-%d %H:%M:%S"
            ))

        else:
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setFormatter(logging.Formatter(
                "%(levelname)s:%(name)s: %(message)s",
                "%Y-%m-%d %H:%M:%S"
            ))

        return handler

    def _set_level(self, logger_level):
        # Allow for an override, mostly for debugging during development.
        # This way a single cog can be isolated if needed.
        if logger_level:
            self._logger_level = logger_level
        else:
            self._logger_level = os.environ['LOGGER_LEVEL'].lower()

        # Set the logging level
        if self._logger_level == "debug":
            self._logger.setLevel(logging.DEBUG)
        elif self._logger_level == "info":
            self._logger.setLevel(logging.INFO)
        elif self._logger_level == "warning":
            self._logger.setLevel(logging.WARNING)
        elif self._logger_level == "error":
            self._logger.setLevel(logging.ERROR)
        elif self._logger_level == "critical":
            self._logger.setLevel(logging.CRITICAL)
        else:
            self._logger.setLevel(logging.ERROR)

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


class MySQLStreamHandler(logging.StreamHandler):
    """docstring for ClassName"""

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.query = """
            INSERT INTO logs (recorded, level, name, message)
            VALUES (%s, %s, %s, %s);
        """

    def write(self, record):
        split_record = record.split("§")
        db = mysql()
        db.execute(self.query, [
            split_record[0],  # asctime
            split_record[1],  # levelname
            split_record[2],  # name
            split_record[3],  # message
        ])
        db.close()
