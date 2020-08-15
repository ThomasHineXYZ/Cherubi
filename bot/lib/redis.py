#!/usr/bin/env python

from dotenv import load_dotenv
from pathlib import Path
import os
import redis

class Redis():
    # Load up the environment variables
    env_file_name = '.env'
    env_path = Path('.') / env_file_name
    load_dotenv(dotenv_path=env_path)

    # Check if .env.local exists, if so, load up those variables, overriding the
    # previously set ones
    local_env_file_name = env_file_name + '.local'
    local_env_path = Path('.') / local_env_file_name
    if os.path.isfile(local_env_file_name):
        load_dotenv(dotenv_path=local_env_path, override=True)

    def __init__(self, prefix = None):
        self._redis = redis.Redis(
            host = os.environ['REDIS_HOST'],
            port = os.environ['REDIS_PORT'],
            db = os.environ['REDIS_DB']
        )
        self._prefix = prefix + ":" if prefix else None

    def __enter__(self):
        return self

    def get(self, key):
        key = self._prefix + key

        information = {}
        information['key'] = key
        information['value'] = self._redis.get(key)
        information['ttl'] = self._redis.ttl(f"{key}")

        print(self._redis.ttl(key))

        return information

    def set(self, key, value, expiry = 0):
        key = self._prefix + key

        if expiry < 0:
            print("You can't have a negative time value")
        elif expiry > 0:
            self._redis.setex(key, expiry, value)
        else:
            self._redis.set(key, value)
