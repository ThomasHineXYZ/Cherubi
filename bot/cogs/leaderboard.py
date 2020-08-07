from discord.ext import commands
from lib.mysql import mysql
import discord
import lib.embedder
import os

class Leaderboard(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(
        name = "leaderboard",
        brief = "Leaderboard for the checklist systems",
        description = "Cherubi Bot - Leaderboards",
        usage = "<shiny>",
        help = "You can add in '--global' to any of the leaderboard subcommands and it will give you the global leaderboards."
    )
    async def leaderboard_group(self, ctx):
        # If no subcommand is given, give the help command for the group
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @leaderboard_group.group(
        name = "shiny",
        brief = "Shiny leader boards for your server",
        description = "Cherubi Bot - Shiny Checklist System (List)",
        help = "This lists off all of the shiny Pokemon in your collection."
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def shiny_subcommand_group(self, ctx):
        # If a subcommand is given, just skip anything else form this command
        if ctx.invoked_subcommand is not None:
            return

        # WIP need to add in an option for global and guild specific. Right now
        # it is just global
        db = mysql()
        query = """
            SELECT
                user_id,
                SUM(count) AS total
            FROM user_shinies
            GROUP BY user_id
            ORDER BY total DESC
            LIMIT 25;
        """
        results = db.query(query)
        db.close()

        columns = {"left": "", "right": ""}
        for result in results:
            columns['left'] += f"{self.client.get_user(result['user_id']).display_name}\n"
            columns['right'] += f"{result['total']}\n"

        fields = [
            ("Name", columns['left'], True),
            ("Count", columns['right'], True),
        ]

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = f"{ctx.guild.name} Shiny Leaderboard",
            fields = fields,
        ))

    @shiny_subcommand_group.group(
        name = "global",
        aliases = ["-global", "--global", "g"],
        brief = "Brief text",
        description = "Cherubi Bot - Shiny Leaderboard (Global)",
        help = "Gets the results for the shiny leader"
    )
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def shiny_subcommand_global(self, ctx):
        # WIP need to add in an option for global and guild specific. Right now
        # it is just global
        db = mysql()
        query = """
            SELECT
                user_id,
                SUM(count) AS total
            FROM user_shinies
            GROUP BY user_id
            ORDER BY total DESC;
        """
        results = db.query(query)
        db.close()

        print(results)
        print(results.values().index(138097615479898112))
        # print(list(results.keys())[list(results.values()).index(138097615479898112)])

        columns = {"left": "", "right": ""}
        for result in results:
            columns['left'] += f"{self.client.get_user(result['user_id']).display_name}\n"
            columns['right'] += f"{result['total']}\n"

        fields = [
            ("Name", columns['left'], True),
            ("Count", columns['right'], True),
            ("Your placing:", "Top 25", False),
        ]

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = "Global Shiny Leaderboard",
            fields = fields,
        ))

def setup(client):
    client.add_cog(Leaderboard(client))
