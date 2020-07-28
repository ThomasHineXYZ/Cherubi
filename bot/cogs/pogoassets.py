from discord.ext import commands
import github
from lib.mysql import mysql
import discord
import os

class PoGoAssets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.github = github.Github(os.environ['GITHUB_ACCESS_TOKEN'])

    def get_newest_commit_id(self, repo):
        branch = repo.get_branch("master")
        return branch.commit.sha

    @commands.command()
    async def run(self, ctx):
        repo = self.github.get_repo("PokeMiners/pogo_assets")
        commit_id = self.get_newest_commit_id(repo)
        await ctx.send(commit_id)

        # In case I need to get a different tree_id later:
        # https://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api/61656698#61656698
        # https://api.github.com/repos/PokeMiners/pogo_assets/git/trees/master?recursive=1
        files = repo.get_git_tree("ace98ff9284529e67c1fa3d1548d953596254b6e").tree

        for file in files:
            print(file.path)

def setup(client):
    client.add_cog(PoGoAssets(client))
