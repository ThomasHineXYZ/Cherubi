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

    def check_commit_hash(self, hash):
        # Grab the current commit hash that we have stored
        db = mysql()
        query = """
            SELECT value
            FROM checks
            WHERE name = %s;
        """
        results = db.query(query, ['pogo_assets_commit_hash'])
        db.close()

        # If the value doesn't doesn't exist in the checks table, add it and say
        # that its a new commit
        if len(results) == 0:
            self.store_commit_hash(hash)
            return True

        # If the grabbed commit hash equals the one that we have stored, it's
        # not a new commit
        if results[0][0] == hash:
            return False

        # Otherwise just assume it's a new commit, it shouldn't hurt anything
        return True

    def store_commit_hash(self, hash):
        db = mysql()
        query = """
            INSERT INTO checks (name, value)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE value = values(value);
        """
        results = db.execute(query, ['pogo_assets_commit_hash', hash])
        db.close()

    def store_pokemon(self, files):
        # Open a connection to the database and set the query up
        db = mysql()
        query = """
            INSERT INTO pogo_pokemon (dex, type, isotope, filename, shiny)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE shiny = values(shiny);
        """

        # Iterate through each of the Pokemon picture files and store them in
        # the table
        for file in files:
            data = self.translate_filename(file.path)
            db.execute(
                query, [
                    data['dex'],
                    data['type'],
                    data['isotope'],
                    data['filename'],
                    data['Shiny'],
                ],
            )

        # Finally close the connection
        db.close()

    def translate_filename(self, filename):
        # Convert the tree / path object to a string
        text = str(filename)

        # Remove the ".png" at the end
        text = text[:-4]

        # If it is a shiny, set it as such and remove the "_shiny"
        shiny = False
        if "_shiny" in text:
            text = text[:-6]
            shiny = True

        # Remove the 'pokemon_icon_' from the beginning of the string
        text = text[13:]

        # Split up the text in to the various sections
        split = text.split("_")

        # If it now starts with 'pm', it's a special Pokemon
        special = False
        specialFilename = None
        if split[0][0:2] == "pm":
            special = True
            split[0] = split[0][2:]
            specialFilename = text

        # Set up the data for returning
        data = {}
        data["dex"] = split[0]
        data["type"] = split[1]

        if special:
            data["isotope"] = split[3]
        elif len(split) == 3:
            data["isotope"] = split[2]
        else:
            data["isotope"] = ""

        data["filename"] = specialFilename
        data["Shiny"] = shiny

        return data

    @tasks.loop(hours = 12)
    async def load_data_from_github(self):
        repo = self.github.get_repo("PokeMiners/pogo_assets")
        commit_hash = self.get_newest_commit_hash(repo)
        new_commit = self.check_commit_hash(commit_hash)

        if not new_commit: # NOTE This is hard set to false for testing
            # In case I need to get a different tree_id later:
            # https://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api/61656698#61656698
            # https://api.github.com/repos/PokeMiners/pogo_assets/git/trees/master?recursive=1
            files = repo.get_git_tree("ace98ff9284529e67c1fa3d1548d953596254b6e").tree

            self.store_pokemon(files)
            for file in files:
                data = self.translate_filename(file.path)

            self.store_commit_hash(commit_hash)
            print("New PoGo Assets commit!")

        else:
            print("No new PoGo Assets commit.")


def setup(client):
    client.add_cog(PoGoAssets(client))
