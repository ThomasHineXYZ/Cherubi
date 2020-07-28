from discord.ext import commands
import github
from lib.mysql import mysql
import discord
import os
import re

class PoGoAssets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.github = github.Github(os.environ['GITHUB_ACCESS_TOKEN'])

    def get_newest_commit_hash(self, repo):
        branch = repo.get_branch("master")
        return branch.commit.sha

    def check_commit_hash(self, sha):
        db = mysql()
        query = """
            SELECT value
            FROM checks
            WHERE name = %s;
        """
        results = db.query(query, ['pogo_assets_commit_hash'])
        db.close()

        if len(results) == 0:
            self.store_commit_hash(sha)
            return True

        if results[0][0] == sha:
            return False

        return True

    def store_commit_hash(self, sha):
        db = mysql()
        query = """
            INSERT INTO checks (name, value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value = values(value);
        """
        results = db.execute(query, ['pogo_assets_commit_hash', sha])
        db.close()

    def translate_filename(self, filename):
        # Convert the tree / path object to a string
        text = str(filename)

        # If it is a shiny, FOR NOW skip it completely
        # WIP maybe have a way to log when the shiny is in the game, but not exactly released yet
        if "_shiny" in text:
            return

        # Remove the 'pokemon_icon_' from the beginning of the string
        text = filename[13:]

        # If it now starts with 'pm', it's a special Pokemon
        if filename[:2] == "pm":
            print(f"Special Pokemon: {text}")

        print(text)

    @commands.command()
    async def run(self, ctx):
        repo = self.github.get_repo("PokeMiners/pogo_assets")
        commit_hash = self.get_newest_commit_hash(repo)
        new_commit = self.check_commit_hash(commit_hash)

        if new_commit == False: # NOTE This is hard set to false for testing
            # In case I need to get a different tree_id later:
            # https://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api/61656698#61656698
            # https://api.github.com/repos/PokeMiners/pogo_assets/git/trees/master?recursive=1
            files = repo.get_git_tree("ace98ff9284529e67c1fa3d1548d953596254b6e").tree

            for file in files:
                self.translate_filename(file.path)

            self.store_commit_hash(commit_hash)
            await ctx.send("New commit!")

        else:
            await ctx.send("No new commit")


def setup(client):
    client.add_cog(PoGoAssets(client))
