from discord.ext import commands, tasks
from lib.mysql import mysql
import discord
import json
import requests

class ShinyData(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.load_data_from_github.start()

    def load_shiny_list(self):
        url = "https://raw.githubusercontent.com/Rplus/Pokemon-shiny/master/assets/pms.json"
        data = json.loads(requests.get(url).text)
        return data

    def store_shiny_list(self, data):
        db = mysql()
        query = """
            INSERT INTO shiny_list (
                dex,
                name_de,
                name_en,
                name_fr,
                name_ja,
                name_kr,
                name_zh,
                type,
                shiny_released,
                released_date,
                fn,
                isotope,
                family
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            ) ON DUPLICATE KEY UPDATE
                shiny_released = VALUES(shiny_released),
                released_date = COALESCE(VALUES(released_date), released_date),
                fn = VALUES(fn),
                isotope = VALUES(isotope),
                family = VALUES(family)
            ;
        """
        for row in data:
            db.execute(query, [
                row['dex'],
                row['name']['de'],
                row['name']['en'],
                row['name']['fr'],
                row['name']['ja'],
                row['name']['kr'],
                row['name']['zh'],
                row.get('type', '_00'),
                row.get('shiny_released', False),
                row.get('released_date', None),
                row.get('fn', None),
                row.get('isotope', ''),
                row['family']
            ])
        db.close()

    @tasks.loop(hours = 12)
    async def load_data_from_github(self):
        print("Updating shiny list")
        data = self.load_shiny_list()
        self.store_shiny_list(data)

    # Makes the load_data_from_github function now start up until the client is ready
    @load_data_from_github.before_loop
    async def before_load_data_from_github(self):
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(ShinyData(client))

# https://raw.githubusercontent.com/Rplus/Pokemon-shiny/master/assets/pms.json
