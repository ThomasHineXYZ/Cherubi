#!/usr/bin/env python

from pathlib import Path
from dotenv import load_dotenv
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

    def __init__(self, prefix=None):
        self._redis = redis.Redis(
            host=os.environ['REDIS_HOST'],
            password=os.environ['REDIS_PASSWORD'] or None,
            port=os.environ['REDIS_PORT'],
            db=os.environ['REDIS_DB']
        )
        self._prefix = prefix + ":" if prefix else ""

    def __enter__(self):
        return self

    def delete(self, key, include_prefix=True):
        if include_prefix:
            key = self._prefix + key

        self._redis.delete(key)

    def deletemulti(self, keys, include_prefix=True):
        for key in keys:
            if isinstance(key, bytes):
                self.delete(key.decode("UTF-8"), include_prefix)
            else:
                self.delete(key, include_prefix)

    def expire(self, key, ttl, include_prefix=True):
        if include_prefix:
            key = self._prefix + key

        self._redis.expire(key, ttl)

    def expiremulti(self, data, include_prefix=True):
        for key, ttl in data:
            if isinstance(key, bytes):
                self.expire(key.decode("UTF-8"), ttl, include_prefix)
            else:
                self.expire(key, ttl, include_prefix)

    def get(self, key, include_prefix=True):
        if include_prefix:
            key = self._prefix + key

        information = {}
        information['key'] = key
        information['value'] = self._redis.get(key)
        information['ttl'] = self._redis.ttl(f"{key}")

        return information

    def getmulti(self, keys, include_prefix=True):
        values = []
        for key in keys:
            if isinstance(key, bytes):
                values.append(self.get(key.decode("UTF-8"), include_prefix))
            else:
                values.append(self.get(key), include_prefix)

        return values

    def keys(self, filter=None):
        return self._redis.keys(
            f"{self._prefix}{filter}" if filter else f"{self._prefix}*"
        )

    def set(self, key, value, expiry=0):
        key = self._prefix + key

        if expiry < 0:
            raise ValueError("You can't have a negative time value.")
        elif expiry > 0:
            self._redis.setex(key, expiry, value)
        else:
            self._redis.set(key, value)

    def setmulti(self, list):
        for key, value, expiry in list:
            self.set(key, value, expiry)
