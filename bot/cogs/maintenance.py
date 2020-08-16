from datetime import datetime
from discord.ext import commands, tasks
from lib.rediswrapper import Redis
import discord


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

        print("Loading maintenance cog")

        self.temp_redis = Redis("temp_message")
        self.temporary_messages.start()

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

            try:
                self.temp_redis.delete(message['key'], False)
                await channel.delete_messages([discord.Object(message_id)])
            except Exception:
                pass


def setup(client):
    client.add_cog(Maintenance(client))
