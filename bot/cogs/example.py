from discord.ext import commands
from lib.mysql import mysql
from lib.rediswrapper import Redis
import discord
import lib.embedder

class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def example(self, ctx):
        await ctx.send('Hoorah!')


def setup(client):
    client.add_cog(Example(client))
