from discord.ext import commands
import discord
import os

class ShinyCheckList(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(
        name = "shiny",
        aliases = ["s"],
        brief = "Shiny checklist system",
        description = "Cherubi Bot - Shiny Checklist System"
    )
    async def shiny_group(self, ctx):
        await ctx.send(str(self.shiny_group.commands))

    @shiny_group.command(
        name = "add",
        brief = "Adds a shiny Pokemon to your list",
        description = "testing again",
        usage = "<Pokemon name or dex number> [number of them]"
    )
    async def add_subcommand(self, ctx):
        await ctx.send("You invoked the `bar` subcommand!")

def setup(client):
    client.add_cog(ShinyCheckList(client))
