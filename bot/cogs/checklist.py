from discord.ext import commands
from lib.mysql import mysql
from typing import Optional
import discord
import lib.embedder
import os

class Checklist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(
        name = "shiny",
        aliases = ["s"],
        brief = "Shiny checklist system",
        description = "Cherubi Bot - Shiny Checklist System",
        usage = "<add | remove | list>"
    )
    async def shiny_group(self, ctx):
        # If no subcommand is given, give the help command for the group
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @shiny_group.command(
        name = "add",
        aliases = ["a"],
        brief = "Adds a shiny Pokemon to your list.",
        description = "Cherubi Bot - Shiny Checklist System (Add)",
        usage = "<name or dex #> [number]",
        help = "You can give either the name or the dex number of the Pokemon to add it to your list.\n\nYou also can give an amount, if you don't it'll add a single one."
    )
    async def add_subcommand(self, ctx, pokemon, count = 1):
        # Just a couple of sanity checks, since I know someone will test this at some point
        if count == 0:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = "Shiny Checklist",
                content = "You can't add 0 of something.",
            ))
            return
        elif count < 0:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = "Shiny Checklist",
                content = "There is no such thing as negative Pokemon. At least... not yet.",
            ))
            return

        # Grab the list of Pokemon for the given name or dex number
        pokemon_data = self.get_pokemon_data(pokemon)

        # If no results are returned, tell the user that that Pokemon doesn't
        # exist.
        # If there is more than one returned value... right now it's a WIP and needs to be dealt with
        # If there is only one response returned than work for it
        if not pokemon_data:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "warning",
                title = "Shiny Checklist",
                content = f"Pokemon `{pokemon}` doesn't exist",
            ))
            return
        elif len(pokemon_data) > 1: # WIP Not implemented right now
            await ctx.send(embed = lib.embedder.make_embed(
                type = "warning",
                title = "Shiny Checklist",
                content = "Pokemon with multiple forms, costumes, or variants aren't supported right now.",
            ))
            return
        else:
            db = mysql()
            query = """
                INSERT INTO user_shinies (user_id, dex, type, isotope, count)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE count = count + VALUES(count);
            """
            db.execute(query, [
                ctx.message.author.id,
                pokemon_data[0]['dex'],
                pokemon_data[0]['type'],
                pokemon_data[0]['isotope'],
                count,
            ])
            db.close()

            # Tell the user that they added the Pokemon successfully to their list
            await ctx.send(embed = lib.embedder.make_embed(
                type = "success",
                title = "Shiny Checklist",
                content = f"Added {count} shiny {pokemon_data[0]['name']} to your list",
                thumbnail = self.generate_image_link(pokemon_data[0], shiny = True)
            ))

    @shiny_group.command(
        name = "remove",
        aliases = ["delete", "r", "d"],
        brief = "Removes a shiny Pokemon from your list.",
        description = "Cherubi Bot - Shiny Checklist System (Remove)",
        usage = "<name or dex #> [number]",
        help = "You can give either the name or the dex number of the Pokemon to remove from your list.\n\nYou also can give an amount, if you don't it'll remove a single one."
    )
    async def remove_subcommand(self, ctx, pokemon, count = 1):
        # Just a couple of sanity checks, since I know someone will test this at some point
        if count == 0:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = "Shiny Checklist",
                content = "You can't remove 0 of something.",
            ))
            return
        elif count < 0:
            count = count * -1

        pokemon_data = self.get_pokemon_data(pokemon)
        if not pokemon_data:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "warning",
                title = "Shiny Checklist",
                content = f"Pokemon `{pokemon}` doesn't exist",
            ))
            return
        elif len(pokemon_data) > 1: # WIP Not implemented right now
            await ctx.send(embed = lib.embedder.make_embed(
                type = "warning",
                title = "Shiny Checklist",
                content = "Pokemon with multiple forms, costumes, or variants aren't supported right now.",
            ))
            return
        else:
            db = mysql()
            query = """
                SELECT count
                FROM user_shinies
                WHERE
                    user_id = %s
                    AND dex = %s
                    AND type = %s
                    AND isotope = %s;
            """
            db.execute(query, [
                ctx.message.author.id,
                pokemon_data[0]['dex'],
                pokemon_data[0]['type'],
                pokemon_data[0]['isotope'],
            ])

            # Check if the user has any of the Pokemon in their list. If they
            # don't, tell them, close the DB and then return.
            #
            # Also check if they have the amount they want to remove, if not,
            # set it to what they have
            result = db.fetchone()
            if (not result) or (result['count'] == 0):
                db.close()
                await ctx.send(embed = lib.embedder.make_embed(
                    type = "warning",
                    title = "Shiny Checklist",
                    content = f"You don't have any shiny {pokemon_data[0]['name']} in your list to remove",
                    thumbnail = self.generate_image_link(pokemon_data[0], shiny = True)
                ))
                return
            elif result['count'] < count:
                count = result['count']

            # If they do however, update the count
            query = """
                UPDATE user_shinies
                SET count = count - %s
                WHERE
                    user_id = %s
                    AND dex = %s
                    AND type = %s
                    AND isotope = %s;
            """
            db.execute(query, [
                count,
                ctx.message.author.id,
                pokemon_data[0]['dex'],
                pokemon_data[0]['type'],
                pokemon_data[0]['isotope'],
            ])
            db.close()

            await ctx.send(embed = lib.embedder.make_embed(
                type = "success",
                title = "Shiny Checklist",
                content = f"Removed {count} shiny {pokemon_data[0]['name']} from your list",
                thumbnail = self.generate_image_link(pokemon_data[0], shiny = True)
            ))

    @shiny_group.command(
        name = "list",
        aliases = ["l"],
        brief = "Lists the shiny Pokemon that you have.",
        description = "Cherubi Bot - Shiny Checklist System (List)",
        help = "This lists off all of the shiny Pokemon in your collection."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def list_subcommand(self, ctx, target: Optional[discord.Member]):
        # If no target is given, use the user who wrote the command
        target = target or ctx.author

        db = mysql()
        query = """
            SELECT
                name.english AS name,
                user_shiny.dex AS dex,
                user_shiny.type AS type,
                user_shiny.isotope AS isotope,
                user_shiny.count AS count
            FROM user_shinies user_shiny
            LEFT JOIN pokemon_names name on name.dex = user_shiny.dex
            WHERE
                user_shiny.user_id = %s
                AND user_shiny.count > 0
            ORDER BY name.english;
        """
        results = db.query(query, [target.id])
        db.close()

        # If the user doesn't have any shiny Pokemon in their list, tell them that
        if not results:
            await ctx.send(embed = lib.embedder.make_embed(
                type = "error",
                title = "Shiny Checklist",
                content = f"Unfortunately {target.display_name} doesn't have any Pokemon in your shiny list...",
            ))

        else:
            columns = {"left": "", "right": ""}
            total_count = 0
            for result in results:
                columns['left'] += f"{result['name']}\n"
                columns['right'] += f"{result['count']}\n"
                total_count += result['count']

            fields = [
                ("Pokemon", columns['left'], True),
                ("Count", columns['right'], True),
                ("Total:", total_count, False),
            ]

            await ctx.send(embed = lib.embedder.make_embed(
                type = "info",
                title = f"{target.display_name}'s Shiny List:",
                fields = fields,
            ))

    @shiny_group.command(
        name = "leaderboard",
        brief = "Lists the shiny Pokemon that you have.",
        description = "Cherubi Bot - Shiny Checklist System (List)",
        help = "This lists off all of the shiny Pokemon in your collection."
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def leaderboard_subcommand(self, ctx):
        # WIP need to add in an option for global and guild specific. Right now
        # it is just global
        db = mysql()
        query = """
            SELECT
                user_id,
                SUM(count) AS total
            FROM user_shinies
            GROUP BY user_id
            ORDER BY total DESC
            LIMIT 25;
        """
        results = db.query(query)
        db.close()

        columns = {"left": "", "right": ""}
        for result in results:
            columns['left'] += f"{self.client.get_user(result['user_id']).display_name}\n"
            columns['right'] += f"{result['total']}\n"

        fields = [
            ("Name", columns['left'], True),
            ("Count", columns['right'], True),
        ]

        await ctx.send(embed = lib.embedder.make_embed(
            type = "info",
            title = "Global Shiny Leaderboard",
            fields = fields,
        ))

    def get_pokemon_data(self, input):
        db = mysql()
        query = """
            SELECT
                pkmn.dex AS 'dex',
                name.english AS 'name',
                pkmn.type AS 'type',
                pkmn.isotope AS 'isotope',
                pkmn.filename AS 'filename',
                pkmn.shiny AS 'shiny'
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
            );
        """
        db.execute(query, [input, input, input, input, input, input, input, input, input, input, input])
        results = db.fetchall()
        db.close()

        return results

    def generate_image_link(self, result, shiny = False):
        # Base url for the repo, plus an image cacher link, if we are using it
        base_url = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Images/Pokemon/"

        url = ""
        url += base_url
        url += "pokemon_icon_"

        # Checks if a unique file name exists for the Pokemon
        if result['filename'] == None: # If no specific file name is given
            # Give it some leading zeroes
            dex = str(result['dex']).zfill(3)

            # base_url + pokemon_icon_{dex}{type}{isotope or ''}_shiny.png
            url += f"{dex}_{result['type']}"

            # If there's an isotope value, add it
            if result['isotope']:
                url += f"_{result['isotope']}"

        else:
            # base_url + pokemon_icon_{fn}_shiny.png
            url += result['filename']

        # If it's shiny, add in that little bit
        if shiny:
            url += "_shiny"

        # Finally, add in the file extension
        url += ".png"

        return url

def setup(client):
    client.add_cog(Checklist(client))
