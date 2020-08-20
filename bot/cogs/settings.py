from datetime import datetime, timedelta
from discord.ext import commands
from lib.mysql import mysql
from lib.rediswrapper import Redis
import lib.embedder
import uuid


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Set up Redis
        self.temp_redis = Redis("temp_message:settings")

    def is_guild_owner():
        def predicate(ctx):
            return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
        return commands.check(predicate)

    @commands.command(
        name="sethome",
        aliases=["setguild", "setserver"],
        brief="Set your home server",
        description="Settings - Set Home Server",
        help="Run this command to change your home server to the one you are currently in"
    )
    @commands.guild_only()
    async def sethome_command(self, ctx):
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

    @commands.command(
        name="setnestchannel",
        brief="Set your server's nest channel",
        description="Settings - Set Nest Channel",
        help="Run this command to change your server's nest channel."
    )
    @commands.guild_only()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def setnestchannel_command(self, ctx):
        # Store the channel ID in the preferences table
        db = mysql()
        query = """
            UPDATE guild_preferences
            SET nest_channel = %s
            WHERE guild = %s;
        """
        db.execute(query, [ctx.channel.id, ctx.guild.id])
        db.close()

        delete_delay = 60
        message = await ctx.send(embed=lib.embedder.make_embed(
            type="info",
            title="Nest Channel Set!",
            content=f"The nest channel for `{ctx.guild}` has been set to `{ctx.channel}`",
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
