from discord.ext import commands
from lib.mysql import mysql
import discord
import os

class Preferences(commands.Cog):
    def __init__(self, client):
        self.client = client

    def user_is_author(ctx):
        return ctx.message.author.id == int(os.environ['BOT_AUTHOR'])

    @commands.command()
    async def preference1(self, ctx):
        db = mysql()
        query = """SELECT name FROM test"""
        test = db.query(query)
        print(test)

        await ctx.send(test[0][0])

    @commands.command()
    @commands.is_owner()
    async def preference2(self, ctx):
        db = mysql()
        query = """SELECT name FROM test"""
        test = db.query(query)
        print(test)

        await ctx.send(test[0][0])

    @commands.command(pass_context = True)
    @commands.check(user_is_me)
    async def preference3(self, ctx):
        db = mysql()
        query = """SELECT name FROM test"""
        test = db.query(query)
        print(test)

        await ctx.send(test[0][0])


def setup(client):
    client.add_cog(Preferences(client))
