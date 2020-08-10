from discord.ext import commands
from lib.mysql import mysql
from typing import Optional
import discord
import lib.embedder
import os

class FriendCode(commands.Cog):
    def __init__(self, client):
        self.client = client

    def is_guild_owner():
        def predicate(ctx):
            return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
        return commands.check(predicate)

    @commands.group(
        name = "friendcode",
        aliases = ["fc"],
        brief = "Friend Code Sharing System",
        description = "Cherubi Bot - Friend Code Sharing System",
        usage = "<add | remove | list>"
    )
    async def friendcode_group(self, ctx, target: Optional[discord.Member]):
        # If a subcommand is given, just skip anything else from this command
        if ctx.invoked_subcommand is not None:
            return

        # If no target is given, use the user who wrote the command
        target = target or ctx.author

        db = mysql()
        query = """
            SELECT
                identifier,
                code
            FROM friend_codes us
            WHERE user_id = %s
            ORDER BY identifier ASC;
        """
        results = db.query(query, [target.id])
        db.close()

        for result in results:
            code = str(result['code']).zfill(12)
            await ctx.send(embed = lib.embedder.make_embed(
                type = "info",
                title = f"F.C. for {result['identifier']}",
                content = code,
                thumbnail = f"https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl={code}",
                footer = f"Owned by {target.display_name}"
            ))

    @friendcode_group.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def example(self, ctx):
        await ctx.send('Hoorah!')

    @friendcode_group.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def listall(self, ctx):
        await ctx.send('Hoorah!')

def setup(client):
    client.add_cog(FriendCode(client))
