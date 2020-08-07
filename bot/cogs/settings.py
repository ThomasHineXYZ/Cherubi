from discord.ext import commands
from lib.mysql import mysql
import discord
import lib.embedder
import os

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name = "sethome",
        aliases = ["setguild"],
        brief = "Set your home server",
        description = "Settings - Set Home Server",
        help = "Run this command to change your home server to the one you are currently in"
    )
    @commands.guild_only()
    async def sethome(self, ctx):
        db = mysql()
        query = """
            INSERT INTO user_preferences (user_id, home_guild)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE home_guild = VALUES(home_guild);
        """
        db.execute(query, [ctx.author.id, ctx.guild.id])
        db.close()

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = "Home Server Set!",
            content = f"Your home server has been set to {ctx.guild.name}.\
                \n\nThe \"home server\" is used for leaderboards and other server specific commands.\
                \n\nTo change this later, just run `{ctx.prefix}sethome` in your main server.",
        ))


def setup(client):
    client.add_cog(Settings(client))
