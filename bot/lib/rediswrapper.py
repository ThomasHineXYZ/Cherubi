#!/usr/bin/env python

from pathlib import Path
from dotenv import load_dotenv
import logging
import os
import redis


class Redis():
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

    def __init__(self, prefix=None):
        try:
            self.logger.debug(f"""
Setting up and connecting.
REDIS_HOST: {os.environ['REDIS_HOST']}
REDIS_PASSWORD: {os.environ['REDIS_PASSWORD'] or None}
REDIS_PORT: {os.environ['REDIS_PORT']}
REDIS_DB: {os.environ['REDIS_DB']}
            """)
            self._redis = redis.Redis(
                host=os.environ['REDIS_HOST'],
                password=os.environ['REDIS_PASSWORD'] or None,
                port=os.environ['REDIS_PORT'],
                db=os.environ['REDIS_DB']
            )
        except Exception:
            self.logger.critical("Redis can't connect to the given system.", exc_info=1)
            raise SystemExit

        # Add the global prefix and given class prefix if any of them are given.
        self._prefix = ""
        self._prefix += os.environ['REDIS_PREFIX'] + ":" if os.environ['REDIS_PREFIX'] else ""
        self._prefix += prefix + ":" if prefix else ""

    def __enter__(self):
        return self

    def delete(self, key, include_prefix=True):
        self.logger.debug("delete: %s, %s", key, include_prefix)

        if include_prefix:
            key = self._prefix + key

        self._redis.delete(key)

    def deletemulti(self, keys, include_prefix=True):
        self.logger.debug("deletemulti: %s, %s", keys, include_prefix)

        for key in keys:
            if isinstance(key, bytes):
                self.delete(key.decode("UTF-8"), include_prefix)
            else:
                self.delete(key, include_prefix)

    def expire(self, key, ttl, include_prefix=True):
        self.logger.debug("expire: %s, %s, %s", key, ttl, include_prefix)

        if include_prefix:
            key = self._prefix + key

        self._redis.expire(key, ttl)

    def expiremulti(self, data, include_prefix=True):
        self.logger.debug("expiremulti: %s, %s", data, include_prefix)

        for key, ttl in data:
            if isinstance(key, bytes):
                self.expire(key.decode("UTF-8"), ttl, include_prefix)
            else:
                self.expire(key, ttl, include_prefix)

    def get(self, key, include_prefix=True):
        self.logger.debug("get: %s, %s", key, include_prefix)

        if include_prefix:
            key = self._prefix + key

        information = {}
        information['key'] = key
        information['value'] = self._redis.get(key)
        information['ttl'] = self._redis.ttl(f"{key}")

        return information

    def getmulti(self, keys, include_prefix=True):
        self.logger.debug("getmulti: %s, %s", keys, include_prefix)

        values = []
        for key in keys:
            if isinstance(key, bytes):
                values.append(self.get(key.decode("UTF-8"), include_prefix))
            else:
                values.append(self.get(key), include_prefix)

        return values

    def keys(self, key_filter=None):
        self.logger.debug("keys: %s", f"{self._prefix}{key_filter}")

        return self._redis.keys(
            f"{self._prefix}{key_filter}" if key_filter else f"{self._prefix}*"
        )

    def set(self, key, value, expiry=0):
        self.logger.debug("set: %s, %s, %s", key, value, expiry)

        key = self._prefix + key

        if expiry < 0:
            raise ValueError("You can't have a negative time value.")
        elif expiry > 0:
            self._redis.setex(key, expiry, value)
        else:
            self._redis.set(key, value)

    def setmulti(self, value_list):
        self.logger.debug("setmulti: %s", value_list)
        for key, value, expiry in value_list:
            self.set(key, value, expiry)
