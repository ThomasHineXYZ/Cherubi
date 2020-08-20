from datetime import datetime, timedelta
from discord.ext import commands
from lib.mysql import mysql
from lib.rediswrapper import Redis
import discord
import lib.embedder
import uuid


class Nest(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("Loading nest cog")

        # Set up Redis
        self.temp_redis = Redis("temp_message:nest")

    def cog_unload(self):
        print("Unloading nest cog")

    @commands.group(
        name="nest",
        aliases=["n"],
        brief="Nest System",
        description="Cherubi Bot - Nest Management System",
        usage="<report>",
        help="You can run the command without a tagged user to bring up your \
info, tag a user to bring up theirs, or run one of the \
subcommands that are below.",
        invoke_without_command=True
    )
    async def nest_group(
        self,
        ctx
    ):
        # Check if this was invoked from a DM or a guild
        if isinstance(ctx.channel, discord.DMChannel):  # DM
            db = mysql()
            query = """
                SELECT
                    up.home_guild,
                    gp.nest_channel
                FROM user_preferences up
                LEFT JOIN guild_preferences gp ON gp.guild = up.home_guild
                WHERE user_id = %s;
            """
            results = db.query(query, [ctx.author.id])
            db.close()

            if not results[0]['home_guild']:
                delete_delay = 60
                message = await ctx.send(embed=lib.embedder.make_embed(
                    type="error",
                    title=f"Your Home Server Isn't Set",
                    content=f"Please set your home server by running `!sethome` in your home server.",
                    footer=f"This message will self-destruct in {delete_delay} seconds"
                ), delete_after=delete_delay)

                expire_time = datetime.now() + timedelta(seconds=delete_delay)
                self.temp_redis.set(
                    str(uuid.uuid4()),
                    f"{ctx.channel.id},{message.id},{expire_time}",
                    0
                )
                return

            if not results[0]['nest_channel']:
                delete_delay = 60
                message = await ctx.send(embed=lib.embedder.make_embed(
                    type="error",
                    title=f"Nest's for {self.client.get_guild(results[0]['home_guild'])}",
                    content=f"Please contact your home server's owner to set up Cherubi's nest system",
                    footer=f"This message will self-destruct in {delete_delay} seconds"
                ), delete_after=delete_delay)

                expire_time = datetime.now() + timedelta(seconds=delete_delay)
                self.temp_redis.set(
                    str(uuid.uuid4()),
                    f"{ctx.channel.id},{message.id},{expire_time}",
                    0
                )
                return

        elif isinstance(ctx.channel, discord.TextChannel):  # Guild
            # Grab the guild's channel ID
            db = mysql()
            query = """
                SELECT
                    nest_channel
                FROM guild_preferences
                WHERE guild = %s;
            """
            results = db.query(query, [ctx.guild.id])
            db.close()

            if not results[0]['nest_channel']:
                delete_delay = 60
                message = await ctx.send(embed=lib.embedder.make_embed(
                    type="info",
                    title=f"Nest's for {ctx.guild}",
                    content=f"Please contact the server owner to set up Cherubi's nest system",
                    footer=f"This message will self-destruct in {delete_delay} seconds"
                ), delete_after=delete_delay)

                expire_time = datetime.now() + timedelta(seconds=delete_delay)
                self.temp_redis.set(
                    str(uuid.uuid4()),
                    f"{ctx.channel.id},{message.id},{expire_time}",
                    0
                )
                return

            text_channel = self.client.get_channel(results[0]['nest_channel'])

            delete_delay = 60
            message = await ctx.send(embed=lib.embedder.make_embed(
                type="info",
                title=f"Nest's for {ctx.guild}",
                content=f"Please see {text_channel.mention} for your server's nests",
                footer=f"This message will self-destruct in {delete_delay} seconds"
            ), delete_after=delete_delay)

            expire_time = datetime.now() + timedelta(seconds=delete_delay)
            self.temp_redis.set(
                str(uuid.uuid4()),
                f"{ctx.channel.id},{message.id},{expire_time}",
                0
            )
        else:  # If it's anything else... just make like nothing happened
            return


def setup(client):
    client.add_cog(Nest(client))
