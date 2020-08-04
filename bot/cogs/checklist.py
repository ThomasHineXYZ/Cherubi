from discord.ext import commands
from lib.mysql import mysql
import discord
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
            ctx.sent("You can't add 0 of something.")
        elif count < 0:
            ctx.sent("There is no such thing as negative Pokemon. At least... not yet.")

        # Grab the list of Pokemon for the given name or dex number
        pokemon_data = self.get_pokemon_data(pokemon)

        # If no results are returned, tell the user that that Pokemon doesn't
        # exist.
        # If there is more than one returned value... right now it's a WIP and needs to be dealt with
        # If there is only one response returned than work for it
        if not pokemon_data:
            await ctx.send(f"Pokemon `{pokemon}` doesn't exist")
            return
        elif len(pokemon_data) > 1: # WIP Not implemented right now
            await ctx.send(f"Pokemon with multiple forms or variants aren't supported right now.")
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
            await ctx.send(f"Added {count} {pokemon_data[0]['name']} to your list")

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
            ctx.sent("You can't remove 0 of something.")
        elif count < 0:
            count = count * -1

        pokemon_data = self.get_pokemon_data(pokemon)
        if not pokemon_data:
            await ctx.send(f"Pokemon `{input}` doesn't exist")
            return
        elif len(pokemon_data) > 1: # WIP Not implemented right now
            await ctx.send(f"Pokemon with multiple forms or variants aren't supported right now.")
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
                await ctx.send(f"You don't have any {pokemon_data[0]['name']} in your list")
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
            await ctx.send(f"Removed {count} {pokemon_data[0]['name']} from your list")

    @shiny_group.command(
        name = "list",
        aliases = ["l"],
        brief = "Lists the shiny Pokemon that you have.",
        description = "Cherubi Bot - Shiny Checklist System (List)",
        help = "This lists off all of the shiny Pokemon in your collection."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def list_subcommand(self, ctx):
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
        results = db.query(query, [ctx.message.author.id])
        db.close()

        # If the user doesn't have any shiny Pokemon in their list, tell them that
        if not results:
            await ctx.send("Unfortunately you don't have any Pokemon in your shiny list...")

        else:
            output = ""
            for result in results:
                output += f"{result['name']}: {result['count']}\n"

            await ctx.send(output)

    @shiny_group.command(
        name = "leaderboard",
        brief = "Lists the shiny Pokemon that you have.",
        description = "Cherubi Bot - Shiny Checklist System (List)",
        help = "This lists off all of the shiny Pokemon in your collection."
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def leaderboard_subcommand(self, ctx):
        pass

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

def setup(client):
    client.add_cog(Checklist(client))
