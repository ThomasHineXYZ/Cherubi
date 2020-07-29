from discord.ext import commands, tasks
from lib.mysql import mysql
import github
import discord
import json
import os
import re
import requests

class PoGoAssets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.load_data_from_github.start()
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
            ON DUPLICATE KEY UPDATE value = VALUES(value);
        """
        results = db.execute(query, ['pogo_assets_commit_hash', hash])
        db.close()

    def store_pokemon_images(self, files):
        # Open a connection to the database and set the query up
        db = mysql()
        query = """
            INSERT INTO pogo_pokemon (dex, type, isotope, filename, shiny)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE shiny = VALUES(shiny);
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
                    data['shiny'],
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
        data["shiny"] = shiny

        return data

    def store_pokemon_name(self, db, dex, language, name):
        queries = {
            "chinese": """
                INSERT INTO pokemon_names_chinese (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "english": """
                INSERT INTO pokemon_names_english (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "french": """
                INSERT INTO pokemon_names_french (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "german": """
                INSERT INTO pokemon_names_german (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "italian": """
                INSERT INTO pokemon_names_italian (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "japanese": """
                INSERT INTO pokemon_names_japanese (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "korean": """
                INSERT INTO pokemon_names_korean (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "portuguese": """
                INSERT INTO pokemon_names_portuguese (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "spanish": """
                INSERT INTO pokemon_names_spanish (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
            "thai": """
                INSERT INTO pokemon_names_thai (dex, name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name);
            """,
        }

        db.execute(queries[language], [dex, bytes(name, 'utf-8').decode()])

    def import_language_files(self):
        # Import / Update the language files from the repo
        language_files = {
            "chinese": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_chinesetraditional.json",
            "english": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_english.json",
            "french": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_french.json",
            "german": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_german.json",
            "italian": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_italian.json",
            "japanese": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_japanese.json",
            "korean": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_korean.json",
            "portuguese": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_brazilianportuguese.json",
            "spanish": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_spanish.json",
            "thai": "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_thai.json"
        }

        # Open a connection to the database and set the query up
        db = mysql()

        # Iterate through each of the language files that were given above
        for language, language_file in language_files.items():
            # Grab the language file, load it as a JSON file, and then use dict and zip to put it in to a proper
            # dictionary, since Niantic is dumb
            data = requests.get(language_file).text
            dump = json.loads(data.encode('utf-8'))
            json_dictionary = dict(
                zip(
                    [a for idx, a in enumerate(dump['data']) if idx % 2 == 0],
                    [a for idx, a in enumerate(dump['data']) if idx % 2 == 1]
                )
            )

            # Iterate through the json_dictionary to find the values that we want
            for json_key, json_value in json_dictionary.items():

                # If it is a a Pokemon name
                # pokemon_name_0001
                if json_key.startswith("pokemon_name_"):
                    dex = json_key[13:]
                    self.store_pokemon_name(db, dex, language, json_value)


        # Finally close the connection
        db.close()

    @tasks.loop(hours = 12)
    async def load_data_from_github(self):
        repo = self.github.get_repo("PokeMiners/pogo_assets")
        commit_hash = self.get_newest_commit_hash(repo)
        new_commit = self.check_commit_hash(commit_hash)

        if new_commit: # NOTE This is hard set to false for testing
            # In case I need to get a different tree_id later:
            # https://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api/61656698#61656698
            # https://api.github.com/repos/PokeMiners/pogo_assets/git/trees/master?recursive=1

            # Store the images of the various Pokemon that are in the repo
            files = repo.get_git_tree("ace98ff9284529e67c1fa3d1548d953596254b6e").tree
            self.store_pokemon_images(files)
            self.store_commit_hash(commit_hash)

            # Import the various language files in case there are any changes
            self.import_language_files()

            print("New PokeMiners/pogo_assets commit!")

        else:
            print("No new PokeMiners/pogo_assets commit.")

    # Makes the load_data_from_github function now start up until the client is ready
    @load_data_from_github.before_loop
    async def before_load_data_from_github(self):
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(PoGoAssets(client))
