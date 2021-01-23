from discord.ext import commands, tasks
from lib.mysql import mysql
import github
import json
import os
import requests


class PoGoAssets(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("Loading pogoassets cog")

        self.load_data_from_github.start()
        self.github = github.Github(os.environ['GITHUB_ACCESS_TOKEN'])

    def cog_unload(self):
        print("Unloading pogoassets cog")

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
        if results[0]['value'] == hash:
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
        db.execute(query, ['pogo_assets_commit_hash', hash])
        db.close()

    def store_pokemon_images(self, files):
        # Open a connection to the database and set the query up
        db = mysql()
        query = """
            INSERT INTO pokemon (dex, type, isotope, filename, shiny)
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

    def import_text_files(self):
        # Import / Update the language files from the repo
        text_file_location = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/"
        text_files = {
            "chinese": f"{text_file_location}/ChineseTraditional.txt",
            "english": f"{text_file_location}/English.txt",
            "french": f"{text_file_location}/French.txt",
            "german": f"{text_file_location}/German.txt",
            "italian": f"{text_file_location}/Italian.txt",
            "japanese": f"{text_file_location}/Japanese.txt",
            "korean": f"{text_file_location}/Korean.txt",
            "portuguese": f"{text_file_location}/BrazilianPortuguese.txt",
            "russian": f"{text_file_location}/Russian.txt",
            "spanish": f"{text_file_location}/Spanish.txt",
            "thai": f"{text_file_location}/Thai.txt",
        }

        # Open a connection to the database and set the query up
        db = mysql()

        # Iterate through each of the language files that were given above
        for language, text_file in text_files.items():
            # Grab the language file, load it as a JSON file, and then use dict and zip to put it in to a proper
            # dictionary, since Niantic is dumb
            data = requests.get(text_file).text

            # Load the text file in to a dictionary
            text_data = self.text_to_dictionary(data)

            # Iterate through the dictionary to find the values we want
            for resource_id, text_value in text_data.items():
                # If it is a a Pokemon name
                # pokemon_name_0001
                if resource_id.startswith("pokemon_name_"):
                    dex = resource_id[13:]
                    if len(dex) == 4:
                        self.store_pokemon_name(db, dex, language, text_value)
                    elif len(dex) == 9:
                        dex = dex[:4]
                        pass  # NOTE: Do something with the mega name
                # If it is a a Pokemon's description
                # pokemon_desc_0001
                elif resource_id.startswith("pokemon_desc_"):
                    dex = resource_id[13:]
                    if len(dex) == 4:
                        self.store_pokemon_descriptions(db, dex, language, text_value)
                    elif len(dex) == 9:
                        dex = dex[:4]
                        pass  # NOTE: Do something with the different forms

        # Finally close the connection
        db.close()

    def text_to_dictionary(self, dump):
        # The different line ending types
        UNIX_NEWLINE = '\n'
        WINDOWS_NEWLINE = '\r\n'
        MAC_NEWLINE = '\r'

        # Convert them all to using Unix line endings
        dump = dump.replace(WINDOWS_NEWLINE, UNIX_NEWLINE)
        dump = dump.replace(MAC_NEWLINE, UNIX_NEWLINE)

        # Split it up by each line break, and then get the length
        dump_split = dump.split("\n\n")
        dump_length = len(dump_split)

        iteration = 0  # The current iteration
        file_dictionary = {}
        for iteration in range(dump_length):
            # Grab the first line. Then remove any unneeded line breaks, the
            # leading bit of text, and clean up any leading/trailing whitespace
            resource_id = dump_split[iteration].split("\n")[0]
            resource_id = resource_id.replace("\n", "")
            resource_id = resource_id.replace("RESOURCE ID:", "")
            resource_id = resource_id.strip()

            # Grab the remaining lines. Remove the leading bit of text, and clean up
            # any leading/trailing whitespace
            other_lines_split = dump_split[iteration].split("\n")[1:]
            text_data = "\n".join(other_lines_split)
            text_data = text_data.replace("TEXT:", "")
            text_data = text_data.strip()

            # Store it in the dictionary
            file_dictionary[resource_id] = text_data

        return file_dictionary

    def store_pokemon_name(self, db, dex, language, name):
        # Create a language dictionary, setting everything as NULL to start.
        name_list = {
            "chinese": None,
            "english": None,
            "french": None,
            "german": None,
            "italian": None,
            "japanese": None,
            "korean": None,
            "portuguese": None,
            "russian": None,
            "spanish": None,
            "thai": None,
        }

        # Set the language that we worked on as the name we grabbed
        name_list[language] = name

        query = """
            INSERT INTO pokemon_names (
                dex,
                chinese,
                english,
                french,
                german,
                italian,
                japanese,
                korean,
                portuguese,
                russian,
                spanish,
                thai
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                chinese = COALESCE(VALUES(chinese), chinese),
                english = COALESCE(VALUES(english), english),
                french = COALESCE(VALUES(french), french),
                german = COALESCE(VALUES(german), german),
                italian = COALESCE(VALUES(italian), italian),
                japanese = COALESCE(VALUES(japanese), japanese),
                korean = COALESCE(VALUES(korean), korean),
                portuguese = COALESCE(VALUES(portuguese), portuguese),
                russian = COALESCE(VALUES(russian), russian),
                spanish = COALESCE(VALUES(spanish), spanish),
                thai = COALESCE(VALUES(thai), thai);
        """

        db.execute(query, [
            dex,
            name_list['chinese'],
            name_list['english'],
            name_list['french'],
            name_list['german'],
            name_list['italian'],
            name_list['japanese'],
            name_list['korean'],
            name_list['portuguese'],
            name_list['russian'],
            name_list['spanish'],
            name_list['thai'],
        ])

    def store_pokemon_descriptions(self, db, dex, language, name):
        # Create a language dictionary, setting everything as NULL to start.
        name_list = {
            "chinese": None,
            "english": None,
            "french": None,
            "german": None,
            "italian": None,
            "japanese": None,
            "korean": None,
            "portuguese": None,
            "russian": None,
            "spanish": None,
            "thai": None,
        }

        # Set the language that we worked on as the name we grabbed
        name_list[language] = name

        query = """
            INSERT INTO pokemon_descriptions (
                dex,
                chinese,
                english,
                french,
                german,
                italian,
                japanese,
                korean,
                portuguese,
                russian,
                spanish,
                thai
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                chinese = COALESCE(VALUES(chinese), chinese),
                english = COALESCE(VALUES(english), english),
                french = COALESCE(VALUES(french), french),
                german = COALESCE(VALUES(german), german),
                italian = COALESCE(VALUES(italian), italian),
                japanese = COALESCE(VALUES(japanese), japanese),
                korean = COALESCE(VALUES(korean), korean),
                portuguese = COALESCE(VALUES(portuguese), portuguese),
                russian = COALESCE(VALUES(russian), russian),
                spanish = COALESCE(VALUES(spanish), spanish),
                thai = COALESCE(VALUES(thai), thai);
        """

        db.execute(query, [
            dex,
            name_list['chinese'],
            name_list['english'],
            name_list['french'],
            name_list['german'],
            name_list['italian'],
            name_list['japanese'],
            name_list['korean'],
            name_list['portuguese'],
            name_list['russian'],
            name_list['spanish'],
            name_list['thai'],
        ])

    @tasks.loop(hours=12)
    async def load_data_from_github(self):
        repo = self.github.get_repo("PokeMiners/pogo_assets")
        commit_hash = self.get_newest_commit_hash(repo)
        new_commit = self.check_commit_hash(commit_hash)

        if new_commit:
            # Iterate through the folders in the master branch of the repo
            for folder in repo.get_git_tree("master").tree:
                # If it's the Images folder, then do things for images
                if folder.path == "Images":
                    for subfolder in repo.get_git_tree(folder.sha).tree:
                        # Store the references of the various Pokemon that are in the repo
                        if subfolder.path == "Pokemon":
                            files = repo.get_git_tree(subfolder.sha).tree
                            self.store_pokemon_images(files)
                            self.store_commit_hash(commit_hash)

            # Import the various language files in case there are any changes
            self.import_text_files()

            print("New PokeMiners/pogo_assets commit!")

        else:
            print("No new PokeMiners/pogo_assets commit.")

    # Makes the load_data_from_github function now start up until the client is ready
    @load_data_from_github.before_loop
    async def before_load_data_from_github(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(PoGoAssets(client))
