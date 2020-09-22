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

    def check_checksum(self, db, api, checksum):
        # Grab the current checksum that we have stored
        query = """
            SELECT value
            FROM checks
            WHERE name = %s;
        """
        results = db.query(query, [f"pogoapi_{api}"])

        # If the value doesn't doesn't exist in the checks table, assume it's
        # new
        if len(results) == 0:
            return True

        # If the grabbed commit hash equals the one that we have stored, it's
        # not a new commit
        if results[0]['value'] == checksum:
            return False

        # Otherwise just assume it's a new commit, it shouldn't hurt anything
        return True

    def store_checksum(self, db, api, checksum):
        query = """
            INSERT INTO checks (name, value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value = VALUES(value);
        """
        db.execute(query, [f"pogoapi_{api}", checksum])

    @commands.command()
    @commands.is_owner()
    async def pogoapi(self, ctx):
        values = self.load_api("v1/api_hashes.json")

        # Set up MySQL. This way it is only a single commit to the server
        db = mysql()

        for value in values:
            new_data = self.check_checksum(db, value, values[value]['hash_sha256'])

            # Check if it's something we want to import, then import it
            if new_data and value == "mega_pokemon.json":
                print("New data for: " + value)

            # Store the new checksum
            if new_data:
                self.store_checksum(db, value, values[value]['hash_sha256'])

        db.close()


def setup(client):
    client.add_cog(PoGoApi(client))
