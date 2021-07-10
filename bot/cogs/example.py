from discord.ext import commands
import discord
import logging
import os


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Set up the logger
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        self.logger.info("Loading example cog")

    def cog_unload(self):
        self.logger.info("Unloading example cog")

    def user_is_author(ctx):
        return ctx.message.author.id == int(os.environ['BOT_AUTHOR'])

    @commands.command()
    @commands.check(user_is_author)
    async def example(self, ctx):
        await ctx.send('Hoorah!')


def setup(client):
    client.add_cog(Example(client))
