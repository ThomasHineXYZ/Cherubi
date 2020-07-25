from discord.ext import commands
from lib.mysql import mysql
import discord
import os

class Preferences(commands.Cog):
    def __init__(self, client):
        self.client = client

    def user_is_author(ctx):
        return ctx.message.author.id == int(os.environ['BOT_AUTHOR'])

    # WIP Technically this works, but right now it requires that the bot
    # restarts for the changes to occur. Will have to fix this up once I
    # eventually get redis working
    @commands.command()
    @commands.is_owner()
    async def changeprefix(self, ctx, prefix):
        # If someone tries to set more than a single character
        if len(prefix) > 1:
            ctx.send("Command prefix can only be a single character")
            return

        # Store the character in the preferences table
        db = mysql()
        query = """
            UPDATE preferences
            SET command_prefix = %s
            WHERE guild = %s;
        """
        db.execute(query, [prefix, ctx.guild.id])
        db.close()

        # Then finally send the user a message saying that it is changed
        await ctx.send(f"Prefix has been changed to: {prefix}")

    @commands.command(pass_context = True)
    @commands.check(user_is_author)
    async def preference3(self, ctx):
        db = mysql()
        query = """SELECT name FROM test"""
        test = db.query(query)
        print(test)

        await ctx.send(test[0][0])


def setup(client):
    client.add_cog(Preferences(client))
