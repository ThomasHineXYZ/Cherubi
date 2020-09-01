from discord.ext import commands, tasks
from lib.mysql import mysql
import requests


class PoGoApi(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("Loading pogoapi cog")

    def cog_unload(self):
        print("Unloading pogoapi cog")

    def load_api(self, api):
        data = requests.get(f"https://pogoapi.net/api/{api}")
        return data.json()

    def check_checksum(self, api, checksum):
        # Grab the current checksum that we have stored
        db = mysql()
        query = """
            SELECT value
            FROM checks
            WHERE name = %s;
        """
        results = db.query(query, [f"pogoapi_{api}"])
        db.close()

        # If the value doesn't doesn't exist in the checks table, add it and say
        # that its a new commit
        if len(results) == 0:
            self.store_commit_hash(hash)
            return True

        # If the grabbed commit hash equals the one that we have stored, it's
        # not a new commit
        if results[0]['value'] == hash:
            return False

        # Otherwise just assume it's a new commit, it shouldn't hurt anything
        return True

    def store_checksum(self, api, checksum):
        db = mysql()
        query = """
            INSERT INTO checks (name, value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value = VALUES(value);
        """
        db.execute(query, [f"pogoapi_{api}", checksum])
        db.close()

    @commands.command()
    @commands.is_owner()
    async def pogoapi(self, ctx):
        values = self.load_api("v1/api_hashes.json")
        for value in values:
            self.store_checksum(value, values[value]['hash_sha256'])


def setup(client):
    client.add_cog(PoGoApi(client))
