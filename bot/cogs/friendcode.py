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
        usage = "[tagged user] | <add>",
        help = "You can run the command without a tagged user to bring up your info, tag a user to bring up theirs, or run one of the subcommands that are below."
    )
    @commands.cooldown(2, 5, commands.BucketType.user)
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
                content = f"Sadly `{target.display_name}` doesn't have any friend codes stored."
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

    @friendcode_group.command(
        name = "add",
        aliases = ["a"],
        brief = "Friend Code Sharing System",
        description = "Cherubi Bot - Friend Code Sharing System",
        usage = "<username> <friend code>",
        help = "This adds the given friend code to your list. If you run this again with the same username, it'll change the friend code for it."
    )
    async def add_subcommand(self, ctx, input_identifier, input_code, input_code_part2 = None, input_code_part3 = None):
        # This and the additional two "input_code" parts are for if the user
        # uses a separated version of the friend code.
        if input_code_part2 is not None:
            input_code = input_code + input_code_part2 + input_code_part3

        # Checks if the identifier if over 16 characters long. If so then send
        # an error embed and return.
        if len(input_identifier) > 16:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = f"Error Adding Friend Code",
                content = "The username / identifier that you gave is longer than the maximum character limit."
            ))
            return

        # Check that the friend code was numbers and that it was 12 digits long,
        # if it isn't then send an error embed and return
        if not input_code.isdigit() or len(input_code) != 12:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = f"Error Adding Friend Code",
                content = "The given friend code isn't 12 numbers long or is not just numbers."
            ))
            await ctx.send_help(str(ctx.command))
            return

        db = mysql()
        query = """
            INSERT INTO friend_codes (user_id, identifier, code)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE code = VALUES(code);
        """
        db.execute(query, [
            ctx.message.author.id,
            input_identifier,
            input_code
        ])
        db.close()

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = f"Added Friend Code",
            content = f"Added friend code `{input_code}` for `{input_identifier}`"
        ))

    @friendcode_group.command(
        name = "list",
        aliases = ["l"],
        brief = "Friend Code Sharing System",
        description = "Cherubi Bot - Friend Code Sharing System",
        help = "This adds the given friend code to your list. If you run this again with the same username, it'll change the friend code for it."
    )
    async def list_subcommand(self, ctx):
        await ctx.send('List All Owner Only Test!')

    @friendcode_group.command(
        name = "listall",
        aliases = ["list_all"],
        brief = "Friend Code Sharing System",
        description = "Cherubi Bot - Friend Code Sharing System",
        help = "This adds the given friend code to your list. If you run this again with the same username, it'll change the friend code for it."
    )
    @commands.check_any(commands.is_owner(), is_guild_owner())
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def listall_subcommand(self, ctx):
        await ctx.send('List All Owner Only Test!')

    @friendcode_group.command(
        name = "remove",
        aliases = ["r"],
        brief = "Friend Code Sharing System",
        description = "Cherubi Bot - Friend Code Sharing System",
        help = "This adds the given friend code to your list. If you run this again with the same username, it'll change the friend code for it."
    )
    async def remove_subcommand(self, ctx):
        await ctx.send('List All Owner Only Test!')


def setup(client):
    client.add_cog(FriendCode(client))
