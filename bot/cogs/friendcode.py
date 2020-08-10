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
        usage = "[tagged user] | <command>",
        help = "You can run the command without a tagged user to bring up your info, tag a user to bring up theirs, or run one of the subcommands that are below."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def friendcode_group(self, ctx, target: Optional[discord.Member]):
        # If a subcommand is given, just skip anything else from this command
        if ctx.invoked_subcommand is not None:
            return

        # If no target is given, use the user who wrote the command
        target = target or ctx.author

        db = mysql()
        query = """
            SELECT
                up.home_guild AS home_guild,
                up.fc_visibility AS visibility,
                fc.identifier AS identifier,
                fc.code AS code
            FROM friend_codes fc
            LEFT JOIN user_preferences up ON up.user_id = fc.user_id
            WHERE fc.user_id = %s
            ORDER BY fc.identifier ASC;
        """
        results = db.query(query, [target.id])
        db.close()

        # Check if the target has any friend codes on file. If not, send a
        # warning embed and return.
        if not results:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "warning",
                title = f"{target.display_name}'s Friend Codes",
                content = f"Sadly `{target.display_name}` doesn't have any friend codes stored.",
            ))
            return

        # Check if the target is the original author,
        # if not then check if their visibility isn't public,
        # if it is then check if this is their home guild.
        # If it isn't, send an error embed and return.
        if target.id != ctx.author.id\
            and results[0]['visibility'] != "public"\
            and results[0]['home_guild'] != ctx.guild.id:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = f"{target.display_name}'s Friend Codes",
                content = f"This is not `{target.display_name}`'s home server and their visibility isn't set to public.",
                footer = f"!sethome or !friendcode visibility public"
            ))
            return

        # For every result returned, send an embed with the friend code and
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
        await ctx.send('List Test!')

def setup(client):
    client.add_cog(FriendCode(client))
