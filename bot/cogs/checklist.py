from discord.ext import commands
from lib.mysql import mysql
import discord
import os

class Checklist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(
        name = "shiny",
        aliases = ["s"],
        brief = "Shiny checklist system",
        description = "Cherubi Bot - Shiny Checklist System",
        usage = "<add | remove | list>"
    )
    async def shiny_group(self, ctx):
        # If no subcommand is given, give the help command for the group
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @shiny_group.command(
        name = "add",
        brief = "Adds a shiny Pokemon to your list",
        description = "Cherubi Bot - Shiny Checklist System (Add)",
        usage = "<name or dex #> [number]",
        help = "You can give either the name or the dex number of the Pokemon to add it to your list.\n\nYou also can give an amount, by default it'll just add just a single one if no number is specified"
    )
    async def add_subcommand(self, ctx, pokemon, number = 1):
        pokemon_data = self.get_pokemon_data(pokemon)
        if not pokemon_data:
            await ctx.send(f"Pokemon `{input}` doesn't exist")
            return
        elif len(pokemon_data) > 1: # WIP Not implemented right now
            await ctx.send(f"Multiple results are implmented right now")
            return
        else:
            await ctx.send(f"{pokemon_data[0]['name']}")


    def get_pokemon_data(self, input):
        db = mysql()
        query = """
            SELECT
                pkmn.dex AS 'dex',
                name.english AS 'name',
                pkmn.type AS 'type',
                pkmn.isotope AS 'isotope',
                pkmn.filename AS 'filename',
                pkmn.shiny AS 'shiny'
            FROM pokemon pkmn
            LEFT JOIN pokemon_names name on name.dex = pkmn.dex
            WHERE (
                pkmn.dex = %s OR
                name.chinese = %s OR
                name.english = %s OR
                name.french = %s OR
                name.german = %s OR
                name.italian = %s OR
                name.japanese = %s OR
                name.korean = %s OR
                name.portuguese = %s OR
                name.spanish = %s OR
                name.thai = %s
            );
        """
        db.execute(query, [input, input, input, input, input, input, input, input, input, input, input])
        results = db.fetchall()
        db.close()

        return results

def setup(client):
    client.add_cog(Checklist(client))
