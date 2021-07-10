from datetime import datetime, timedelta
from discord.ext import commands
from lib.mysqlwrapper import mysql
from lib.rediswrapper import Redis
import lib.embedder
import logging
import uuid


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Set up the logger
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        self.logger.info("Loading settings cog")

        # Set up Redis
        self.temp_redis = Redis("temp_message:settings")

    def cog_unload(self):
        self.logger.info("Unloading settings cog")

    @commands.command(
        name="sethome",
        aliases=["setguild", "setserver"],
        brief="Set your home server",
        description="Settings - Set Home Server",
        help="Run this command to change your home server to the one you \
are currently in"
    )
    @commands.guild_only()
    async def sethome(self, ctx):
        db = mysql()
        query = """
            INSERT INTO user_preferences (user_id, home_guild)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE home_guild = VALUES(home_guild);
        """
        db.execute(query, [ctx.author.id, ctx.guild.id])
        db.close()

        delete_delay = 120
        message = await ctx.send(embed=lib.embedder.make_embed(
            type="info",
            title="Home Server Set!",
            content=f"Your home server has been set to `{ctx.guild.name}`.\
                \n\nThe \"home server\" is used for leaderboards and other server specific commands.\
                \n\nTo change this later, just run `{ctx.prefix}sethome` in your main server.",
            footer=f"This message will self-destruct in {delete_delay} seconds"
        ), delete_after=delete_delay)

        expire_time = datetime.now() + timedelta(seconds=delete_delay)
        self.temp_redis.set(
            str(uuid.uuid4()),
            f"{ctx.channel.id},{message.id},{expire_time}",
            0
        )


def setup(client):
    client.add_cog(Settings(client))
