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
        # test = repo.create_git_tree([
        #     github.InputGitTreeElement(
        #         "Images/Pokemon",
        #         "100644",
        #         "blob",
        #         #content="File created by PyGithub"
        #     )
        # ])

        # print(test)

        branch = repo.get_branch("master")
        await ctx.send(branch)

def setup(client):
    client.add_cog(PoGoAssets(client))
