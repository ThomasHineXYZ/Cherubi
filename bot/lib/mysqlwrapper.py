#!/usr/bin/env python

from dotenv import load_dotenv
from mysql import connector
from pathlib import Path
import os
import logging


class mysql():
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

    # Set up logger. If it fails, then exit.
    # We're using the qualname here so that it's separate from other libs,
    # since using it to store stuff for logger can cause a recursion issue.
    try:
        logger = logging.getLogger(__qualname__)
        logger.addHandler(logging.NullHandler())
    except Exception as e:
        print(e)
        raise SystemExit

    def __init__(self):
        try:
            self.logger.debug(f"""
Setting up and connecting.
MYSQL_HOST: {os.environ['MYSQL_HOST']}
MYSQL_USER: {os.environ['MYSQL_USER']}
MYSQL_PASS: {os.environ['MYSQL_PASS']}
MYSQL_DBNAME: {os.environ['MYSQL_DBNAME']}
MYSQL_PORT: {os.environ['MYSQL_PORT']}
            """)
            self._db = connector.connect(
                host=os.environ['MYSQL_HOST'],
                user=os.environ['MYSQL_USER'],
                password=os.environ['MYSQL_PASS'],
                database=os.environ['MYSQL_DBNAME'],
                port=os.environ['MYSQL_PORT']
            )
            self._cursor = self._db.cursor(dictionary=True)
            self.logger.debug("MySQL connected successfully.")
        except Exception:
            self.logger.critical("MySQL can't connect to the given database.", exc_info=1)
            raise SystemExit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._db

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.logger.debug("execute:\n[Query: %s]\n[Params: %s]", sql, params)
        self.cursor.execute(sql, params or ())

    def executemany(self, sql, params=None):
        self.logger.debug("executemany:\n[Query: %s]\n[Params: %s]", sql, params)
        self.cursor.executemany(sql, params or ())

    def fetchall(self):
        self.logger.debug("fetchall")
        return self.cursor.fetchall()

    def fetchone(self):
        self.logger.debug("fetchone")
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.logger.debug("query:\n[Query: %s]\n[Params: %s]", sql, params)
        self.cursor.execute(sql, params or ())
        return self.fetchall()
