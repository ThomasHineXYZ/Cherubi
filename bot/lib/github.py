#!/usr/bin/env python

from dotenv import load_dotenv
from pathlib import Path
import os
import requests

class github():
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

    def __init__(self):
        self._headers = {"Authorization": os.environ['GITHUB_ACCESS_TOKEN']}

    def __enter__(self):
        return self

    def run_query(self, query):
        request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=self._headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
