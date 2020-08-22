from datetime import datetime, timedelta
from discord.ext import commands
from lib.mysql import mysql
from lib.rediswrapper import Redis
from typing import Optional
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

    def is_guild_owner():
        def predicate(ctx):
            return ctx.guild is not None and \
                ctx.guild.owner_id == ctx.author.id
        return commands.check(predicate)

    @commands.group(
        name="nest",
        brief="Nest System",
        description="Cherubi Bot - Nest Management System",
        usage="<report>",
        help="",
        invoke_without_command=True
    )
    async def nest_group(self, ctx):
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
                delete_delay = 120
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
                delete_delay = 120
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

            pass  # WIP

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

    @nest_group.command(
        name="add",
        aliases=["a"],
        brief="Nest System",
        description="Cherubi Bot - Nest Management System",
        usage="<add> <\"name of the nest\"> [latitude] [longitude]",
        help="You can run the command without a tagged user to bring up your \
info, tag a user to bring up theirs, or run one of the \
subcommands that are below.",
        invoke_without_command=True
    )
    @commands.check_any(
        commands.is_owner(),
        is_guild_owner(),
        commands.has_role("Admin"),
        commands.has_role("Nest"),
        commands.has_role("Owner"),
        commands.has_role("Staff"),
        commands.has_role("Tech")
    )
    @commands.guild_only()
    async def nest_add_subcommand(self, ctx, name, latitude: Optional[str], longitude: Optional[str]):
        db = mysql()
        query = """
            INSERT INTO nests (guild, name, latitude, longitude, added)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                added = VALUES(added);
        """
        db.execute(query, [
            ctx.message.guild.id,
            name,
            None,  # WIP: Latitude
            None  # WIP: Longitude
        ])
        db.close()


def setup(client):
    client.add_cog(Nest(client))
