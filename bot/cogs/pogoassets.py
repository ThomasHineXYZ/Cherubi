from discord.ext import commands
from lib.mysql import mysql
from lib.github import github
import discord
import os

class PoGoAssets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.github = github

    @commands.command()
    async def run(self, ctx):
        await ctx.send("github test")
        query = """
{
  repository(owner: "PokeMiners", name: "pogo_assets") {
    pushedAt
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
        """
        await ctx.send(self.github().run_query(query))

def setup(client):
    client.add_cog(PoGoAssets(client))
