from datetime import datetime
from discord.ext import commands, tasks
from lib.mysqlwrapper import mysql
from lib.rediswrapper import Redis
from prettytable import PrettyTable
import discord
import lib.embedder
import logging
import os


class Maintenance(commands.Cog):
    """Cog for running maintenance task loops

    This is where all of the various maintenance tasks will reside for Cherubi

    Attributes:
        client: Sets up the client / bot for local access within the cog
        temp_redis: Sets up the "temp_message" Redis connector
    Extends:
        commands.Cog
    """

    def __init__(self, client):
        self.client = client

        # Set up the loggers
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        self.logger.info("Loading maintenance cog")

        self.temp_redis = Redis("temp_message")
        self.missing_pokemon_form_names.start()
        self.temporary_messages.start()

        # If the user isn't using the MySQL logger, then don't bother trying to
        # clean it.
        if os.environ['LOGGER_STREAM'].lower() == "mysql":
            self.clean_mysql_logs.start()

    def cog_unload(self):
        self.logger.info("Unloading maintenance cog")
        self.clean_mysql_logs.stop()
        self.missing_pokemon_form_names.stop()
        self.temporary_messages.stop()

    @tasks.loop(count=1)
    async def clean_mysql_logs(self):
        """Cleans up old log entries

        This cleans up any old logs. Keeping only the last month, or two months
        for critical ones.

        Loop count is set to 1 so that it only runs on start up. Any more and that
        would just be excessive.
        """

        # Counter for all of the logs that were cleaned up
        count = 0

        # Initiate the database
        db = mysql()

        # Clean non-critical logs
        query = """
            DELETE FROM logs
            WHERE recorded < DATE_SUB(NOW(), INTERVAL 1 MONTH)
                AND level != 'CRITICAL';
        """
        db.execute(query)
        count += db.cursor.rowcount

        # Clean critical logs
        query = """
            DELETE FROM logs
            WHERE recorded < DATE_SUB(NOW(), INTERVAL 2 MONTH)
                AND level = 'CRITICAL';
        """
        db.execute(query)
        count += db.cursor.rowcount

        # Close the database
        db.close()

        # Log how many logs were removed
        self.logger.info(f"Cleaned up {count} old logs.")

    @tasks.loop(hours=6)
    async def missing_pokemon_form_names(self):
        """Sends a DM when there are forms that need names

        Creates a neat little ASCII table with the list of all of the Pokemon
        that are needing names for their forms.
        """
        db = mysql()
        query = """
            SELECT pkmn.dex AS 'dex',
                name.english AS 'english',
                pkmn.type AS 'type',
                pkmn.isotope AS 'isotope',
                pkmn.filename AS 'filename'

            FROM pokemon pkmn
            LEFT JOIN pokemon_names name ON name.dex = pkmn.dex
            LEFT JOIN pokemon_form_names form_name
                ON form_name.dex = pkmn.dex
                AND form_name.type = pkmn.type

            WHERE pkmn.type != "00"
            AND form_name.name IS NULL
            AND pkmn.dex != 327;
        """  # Ignore Spinda types, since they are dumb
        results = db.query(query)
        db.close()

        # If no results were returned, just skip everything below
        if not results:
            return

        # Set up and generate the ASCII table
        table = PrettyTable()
        table.field_names = results[0].keys()
        for result in results:
            table.add_row(result.values())

        # Finally print out the table in a codeblock and DM it to me
        owner_user = self.client.get_user(self.client.owner_id)
        await owner_user.send(embed=lib.embedder.make_embed(
            type="info",
            title="Missing Pokemon Form Information",
            content=f"```{table}```"
        ))

    @missing_pokemon_form_names.before_loop
    async def before_missing_pokemon_form_names(self):
        """Waits until the bot is ready

        This just makes it so that the loop doesn't start until the bot is
        completely ready to run
        """
        await self.client.wait_until_ready()

    @tasks.loop(seconds=60)
    async def temporary_messages(self):
        """Cleans up any expired messages in Redis

        Checks every minute if any of the temporary messages in the Redis
        buffer have expired or not. If they have, delete the entry from it.
        """
        # Cleanup any messages that were (hopefully) already autodeleted by the
        # `delete_after` value
        keys = self.temp_redis.keys()
        messages = self.temp_redis.getmulti(keys, False)
        for message in messages:
            # Convert the data received from Redis in to a usable set of values
            decoded_message = message['value'].decode("UTF-8")
            split_message = decoded_message.split(",")
            expire_datetime = split_message[2]

            # If the expire time should have happened already, just delete it
            # from Redis
            if datetime.now() >= datetime.strptime(
                expire_datetime,
                "%Y-%m-%d %H:%M:%S.%f"
            ):
                self.temp_redis.delete(message['key'], False)

    @temporary_messages.before_loop
    async def before_temporary_messages(self):
        """Cleans up old messages from before the bot getting shut down

        This runs after the bot starts up, but before the temporary message
        checker starts running. It deletes any messages that are in the
        temporary message "buffer" when the bot starts up.
        """
        # Wait for the bot to be connected and ready otherwise this will fail
        await self.client.wait_until_ready()

        # Cleanup any old messages that are still showing as up according to
        # Redis
        keys = self.temp_redis.keys()
        messages = self.temp_redis.getmulti(keys, False)
        for message in messages:
            # Convert the data received from Redis in to a usable set of values
            decoded_message = message['value'].decode("UTF-8")
            split_message = decoded_message.split(",")
            channel_id = int(split_message[0])
            message_id = int(split_message[1])

            # Find the Discord channel, and then delete the message(s) in it.
            # It's in a try/except so that any exceptions can be ignored.
            channel = self.client.get_channel(channel_id)

            # NOTE ** This doesn't work for DMs.**
            # Might be something to look in to later. But as of right now it's
            # not a huge concern.
            try:
                self.temp_redis.delete(message['key'], False)
                await channel.delete_messages([discord.Object(message_id)])
            except Exception:
                pass

        self.logger.info(f"{len(keys)} temporary messages were cleaned up.")

    @temporary_messages.after_loop
    async def after_temporary_messages(self):
        keys = self.temp_redis.keys()
        self.logger.info(f"{len(keys)} temporary messages waiting for cleanup.")


def setup(client):
    client.add_cog(Maintenance(client))
