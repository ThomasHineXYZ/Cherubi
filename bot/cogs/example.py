from discord.ext import commands
import discord
import os


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

    def user_is_author(ctx):
        return ctx.message.author.id == int(os.environ['BOT_AUTHOR'])

    @commands.command()
    @commands.check(user_is_author)
    async def example(self, ctx):
        await ctx.send('Hoorah!')


def setup(client):
    client.add_cog(Example(client))
