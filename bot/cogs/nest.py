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

    def generate_image_link(self, dex):
        # Base url for the repo, plus an image cacher link, if we are using it
        base_url = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Images/Pokemon/"

        url = base_url
        url += "pokemon_icon_"

        # Give it some leading zeroes
        dex = str(dex).zfill(3)

        # Assume the variant of it is '00' since it really doesn't matter
        url += f"{dex}_00"

        # Finally, add in the file extension
        url += ".png"

        return url

    def get_nest_info(self, guild_id, location):
        db = mysql()
        query = """
            SELECT
                name,
                added
            FROM nests
            WHERE guild = %s
                AND name = %s
            LIMIT 1;
        """
        db.execute(query, [guild_id, location])
        results = db.fetchall()
        db.close()

        return results

    def get_pokemon_data(self, input):
        db = mysql()
        query = """
            SELECT
                pkmn.dex AS 'dex',
                name.english AS 'name'
            FROM pokemon pkmn
            LEFT JOIN pokemon_names name on name.dex = pkmn.dex
            WHERE (
                pkmn.dex = %s OR
                name.chinese = %s OR
                name.english = %s OR
                name.french = %s OR
                name.german = %s OR
                name.italian = %s OR
                name.japanese = %s OR
                name.korean = %s OR
                name.portuguese = %s OR
                name.spanish = %s OR
                name.thai = %s
            )
            LIMIT 1;
        """
        db.execute(query, [input, input, input, input, input, input, input, input, input, input, input])
        results = db.fetchall()
        db.close()

        return results

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
            # Grab the guild's nest channel ID
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
                    type="error",
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
        brief="Add a nest to your server",
        description="Cherubi Bot - Nest Management System",
        usage="<add> <\"name of the nest\"> [latitude] [longitude]",
        help="Adds a nest location to your server. You can provide GPS coordinates if you'd like"
            # WIP latitude longitude
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
        # Grab the guild's nest channel ID
        db = mysql()
        query = """
            SELECT
                nest_channel
            FROM guild_preferences
            WHERE guild = %s;
        """
        results = db.query(query, [ctx.guild.id])
        db.close()

        # Check if the nests channel is even set. If not, then error out and tell the user to set the nests channel
        if not results[0]['nest_channel']:
            delete_delay = 60
            message = await ctx.send(embed=lib.embedder.make_embed(
                type="error",
                title=f"Nest's for {ctx.guild}",
                content=f"Set the nests channel by running `{ctx.prefix}nest setchannel` in your desired channel.",
                footer=f"This message will self-destruct in {delete_delay} seconds"
            ), delete_after=delete_delay)

            expire_time = datetime.now() + timedelta(seconds=delete_delay)
            self.temp_redis.set(
                str(uuid.uuid4()),
                f"{ctx.channel.id},{message.id},{expire_time}",
                0
            )
            return

        # Remove any accidental whitespace at the beginning or end of the name
        name = name.strip()

        # Do checks on the name
        # Check if the name is either blank or empty
        if len(name) == 0 or not name:
            delete_delay = 60
            message = await ctx.send(embed=lib.embedder.make_embed(
                type="error",
                title=f"Nest's for {ctx.guild}",
                content=f"You need to provide a valid, and not blank, name for the nest.",
                footer=f"This message will self-destruct in {delete_delay} seconds"
            ), delete_after=delete_delay)

            expire_time = datetime.now() + timedelta(seconds=delete_delay)
            self.temp_redis.set(
                str(uuid.uuid4()),
                f"{ctx.channel.id},{message.id},{expire_time}",
                0
            )
            return

        # Check if the name of the nest is over the alloted 32 characters
        if len(name) > 32:
            delete_delay = 60
            message = await ctx.send(embed=lib.embedder.make_embed(
                type="error",
                title=f"Nest's for {ctx.guild}",
                content=f"The name for the nest is over the 32 character limit.\nIt was {len(name)} characters long.",
                footer=f"This message will self-destruct in {delete_delay} seconds"
            ), delete_after=delete_delay)

            expire_time = datetime.now() + timedelta(seconds=delete_delay)
            self.temp_redis.set(
                str(uuid.uuid4()),
                f"{ctx.channel.id},{message.id},{expire_time}",
                0
            )
            return

        db = mysql()
        query = """
            INSERT INTO nests (guild, name, latitude, longitude, added)
            VALUES (%s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude);
        """
        db.execute(query, [
            ctx.message.guild.id,
            name,
            None,  # WIP: Latitude: https://en.wikipedia.org/wiki/ISO_6709
            None  # WIP: Longitude
        ])
        db.close()

        delete_delay = 60
        message = await ctx.send(embed=lib.embedder.make_embed(
            type="info",
            title=f"Nest's for {ctx.guild}",
            content=f"Added `{name}` to your server's nests",
            footer=f"This message will self-destruct in {delete_delay} seconds"
        ), delete_after=delete_delay)

        expire_time = datetime.now() + timedelta(seconds=delete_delay)
        self.temp_redis.set(
            str(uuid.uuid4()),
            f"{ctx.channel.id},{message.id},{expire_time}",
            0
        )

    @nest_group.command(
        name="list",
        aliases=["l"],
        brief="Add a nest to your server",
        description="Cherubi Bot - Nest Management System",
        help="Lists the nests for your server"
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
    async def nest_list_subcommand(self, ctx):
        db = mysql()
        query = """
            SELECT
                nest.name AS 'name',
                nest.latitude AS 'latitude',
                nest.longitude AS 'longitude',
                pkmnname.english AS pokemon_name,
                nest.reported_by AS reported_by,
                nest.reported AS reported
            FROM nests nest
            LEFT JOIN pokemon_names pkmnname ON pkmnname.dex = nest.pokemon
            WHERE guild = %s
            ORDER BY nest.name;
        """
        results = db.query(query, [ctx.guild.id])
        db.close()

        fields = []
        for result in results:
            data = ""
            # If a latitude is set, add it
            if result['latitude']:
                data += "\n" + "**Latitude**: " + result['latitude']

            # If a longitude is set, add it
            if result['longitude']:
                data += "\n" + "**Longitude**: " + result['longitude']

            # If a Pokemon was reported, add in the Pokemon's name
            if result['pokemon_name']:
                data += "\n" + "**Pokémon**: " + str(result['pokemon_name'])

            # Add in the person's nickname, username, or ID if there was a
            # Pokemon that got reported for that nest
            if result['reported_by']:
                # This is here in case someone reported a nest and then left the
                # guild
                if ctx.guild.get_member(result['reported_by']):
                    data += "\n" + "**Reported By**: " + \
                        str(ctx.guild.get_member(result['reported_by']).display_name)

                elif self.client.get_user(result['reported_by']):
                    data += "\n" + "**Reported By**: " + \
                        str(self.client.get_user(result['reported_by']))

                else:
                    data += "\n" + "**Reported By (id)**: " + str(result['reported_by'])

            # Put in the datetime for when the nest got a report
            if result['reported']:
                data += "\n" + "**Reported**: " + str(result['reported'])

            if not data:
                data = u"\u200B"

            fields.append((f"__{result['name']}__", data, True))

        fields.append(lib.embedder.separator)

        fields.append(["Number of Nests:", len(results), True])

        delete_delay = 60
        message = await ctx.send(embed=lib.embedder.make_embed(
            type="info",
            title=f"Nest's for {ctx.guild}",
            content=f"Here are the list of nests that are on your server currently:",
            fields=fields,
            footer=f"This message will self-destruct in {delete_delay} seconds"
        ), delete_after=delete_delay)

        expire_time = datetime.now() + timedelta(seconds=delete_delay)
        self.temp_redis.set(
            str(uuid.uuid4()),
            f"{ctx.channel.id},{message.id},{expire_time}",
            0
        )

    @nest_group.command(
        name="report",
        aliases=["r"],
        brief="Reports a Pokémon in a nest for your server",
        description="Cherubi Bot - Nest Management System",
        help="Reports a nested Pokémon for your server"
    )
    @commands.guild_only()
    async def nest_report_subcommand(self, ctx, *args):
        await ctx.message.delete()

        # Convert the tuple of arguments in to a much nicer list
        arguments = list(args)

        # Search for the Pokemon using the first value that was given
        results_pokemon = self.get_pokemon_data(arguments[0])

        # If something was returned, remove it from the list.
        # If nothing was returned, try using the last given value just in case.
        if results_pokemon:
            arguments.remove(arguments[0])
        else:
            results_pokemon = self.get_pokemon_data(arguments[-1])
            # If data was returned, remove the last argument
            if results_pokemon:
                arguments.remove(arguments[-1])

        # If nothing is still returned, tell the user they didn't give a valid Pokemon
        if not results_pokemon:
            delete_delay = 120
            message = await ctx.send(embed=lib.embedder.make_embed(
                type="error",
                title=f"Nest's for {ctx.guild}",
                content=f"No valid Pokemon was given.",
                footer=f"This message will self-destruct in {delete_delay} seconds"
            ), delete_after=delete_delay)

            expire_time = datetime.now() + timedelta(seconds=delete_delay)
            self.temp_redis.set(
                str(uuid.uuid4()),
                f"{ctx.channel.id},{message.id},{expire_time}",
                0
            )
            return

        # Join the remaining arguments together for use as the location
        location = " ".join(arguments)

        # Find the nest using the location given
        results_location = self.get_nest_info(ctx.guild.id, location)

        # If it failed to find one and there's an ampersand in the location
        # string, replace it with the word 'and' and try again
        if not results_location and " & " in location:
            location = location.replace(" & ", " and ")

            results_location = self.get_nest_info(ctx.guild.id, location)

        # Now the opposite, just in case
        if not results_location and " and " in location:
            location = location.replace(" and ", " & ")

            results_location = self.get_nest_info(ctx.guild.id, location)

        # If there still is no returned value, tell the user the location wasn't valid
        if not results_location:
            delete_delay = 120
            message = await ctx.send(embed=lib.embedder.make_embed(
                type="error",
                title=f"Nest's for {ctx.guild}",
                content="No valid nest location was given.",
                footer=f"This message will self-destruct in {delete_delay} seconds"
            ), delete_after=delete_delay)

            expire_time = datetime.now() + timedelta(seconds=delete_delay)
            self.temp_redis.set(
                str(uuid.uuid4()),
                f"{ctx.channel.id},{message.id},{expire_time}",
                0
            )
            return

        # Add in the new report
        db = mysql()
        query = """
            UPDATE nests
            SET pokemon = %s,
                reported_by = %s,
                reported = NOW()
            WHERE guild = %s
            AND name = %s;
        """
        db.execute(query, [results_pokemon[0]['dex'], ctx.author.id, ctx.guild.id, results_location[0]['name']])
        db.close()

        delete_delay = 120
        message = await ctx.send(embed=lib.embedder.make_embed(
            type="success",
            title=f"Nest's for {ctx.guild}",
            content=f"Reported `{results_pokemon[0]['name']}` at `{results_location[0]['name']}`",
            thumbnail=self.generate_image_link(results_pokemon[0]['dex']),
            footer=f"This message will self-destruct in {delete_delay} seconds"
        ), delete_after=delete_delay)

        expire_time = datetime.now() + timedelta(seconds=delete_delay)
        self.temp_redis.set(
            str(uuid.uuid4()),
            f"{ctx.channel.id},{message.id},{expire_time}",
            0
        )


def setup(client):
    client.add_cog(Nest(client))
