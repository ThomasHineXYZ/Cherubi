from discord.ext import commands
import discord

class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def example(self, ctx):
        await ctx.send('Hoorah!')

def setup(client):
    client.add_cog(Example(client))
