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
        # If a subcommand is given, just skip anything else from this command
        if ctx.invoked_subcommand is not None:
            return

        # WIP need to add in an option for global and guild specific. Right now
        # it is just global
        db = mysql()
        query = """
            SELECT
                us.user_id,
                home_guild,
                SUM(us.count) AS total
            FROM user_shinies us
            JOIN user_preferences up ON up.user_id = us.user_id
            WHERE home_guild = %s
            GROUP BY user_id
            ORDER BY total DESC;
        """
        results = db.query(query, [ctx.guild.id])
        db.close()

        columns = {"left": "", "right": ""}
        for result in results[:10]:
            columns['left'] += f"{self.client.get_user(result['user_id']).display_name}\n"
            columns['right'] += f"{result['total']}\n"

        rank = self.find_user_place(ctx.author.id, results)

        fields = [
            ("Name", columns['left'], True),
            ("Count", columns['right'], True),
            lib.embedder.separator,
            ("Your Rank:", rank, True),
            ("Your Count", results[rank-1]['total'], True),
        ]

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = f"{ctx.guild.name} Shiny Leaderboard",
            fields = fields,
        ))

    @shiny_subcommand_group.group(
        name = "global",
        aliases = ["-global", "--global", "-g", "g"],
        brief = "Brief text",
        description = "Cherubi Bot - Shiny Leaderboard (Global)",
        help = "Gets the results for the shiny leader"
    )
    @commands.cooldown(1, 60, commands.BucketType.guild)
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

        columns = {"left": "", "right": ""}
        for result in results[:25]:
            columns['left'] += f"{self.client.get_user(result['user_id']).display_name}\n"
            columns['right'] += f"{result['total']}\n"

        rank = self.find_user_place(ctx.author.id, results)

        fields = [
            ("Name:", columns['left'], True),
            ("Count:", columns['right'], True),
            lib.embedder.separator,
            ("Your Rank:", rank, True),
            ("Your Count", results[rank-1]['total'], True),
        ]

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = "Global Shiny Leaderboard",
            fields = fields,
        ))

    def find_user_place(self, user_id, results):
        return next((i for i, item in enumerate(results) if item["user_id"] == user_id), None) + 1

def setup(client):
    client.add_cog(Leaderboard(client))
