from discord.ext import commands
import github
from lib.mysql import mysql
import discord
import os

class PoGoAssets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.github = github.Github(os.environ['GITHUB_ACCESS_TOKEN'])

    @commands.command()
    async def run(self, ctx):
        repo = self.github.get_repo("PokeMiners/pogo_assets")
        branch = repo.get_branch("master")
        contents = repo.get_contents("Images/Pokemon/")
        for file in contents:
            print(file.path)
        await ctx.send(branch.commit)

def setup(client):
    client.add_cog(PoGoAssets(client))
