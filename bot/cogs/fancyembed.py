from discord.ext import commands
from lib.mysql import mysql
import lib.embedder
import logging


class FancyEmbed(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Set up the logger
        self.logger = logging.getLogger(__name__)

        self.logger.info("Loading fancyembed cog")

    def cog_unload(self):
        self.logger.info("Unloading fancyembed cog")

    @commands.command(
        brief="Shows you a picture of the shiny Pokémon you give",
        usage="<pokemon>"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def shinyembed(self, ctx, *, input):
        results = self.get_pokemon_info(input)
        if len(results) > 1:
            # TODO make a selection for people to choose which one they mean
            for result in results:
                sprite = self.generate_sprite_link(result, True)
                image = self.generate_image_link(result, True)
                embed = self.generate_embed(ctx, sprite, image, result)
                await ctx.send(embed=embed)
        elif len(results) == 0:
            await ctx.send(f"Pokemon `{input}` doesn't exist")
        else:
            sprite = self.generate_sprite_link(results[0], True)
            image = self.generate_image_link(results[0], True)
            embed = self.generate_embed(ctx, sprite, image, results[0])
            await ctx.send(embed=embed)

    @commands.command(
        brief="Shows you a picture of the Pokémon you give",
        usage="<pokemon>"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def normalembed(self, ctx, *, input):
        results = self.get_pokemon_info(input)
        if len(results) > 1:
            # TODO make a selection for people to choose which one they mean
            for result in results:
                sprite = self.generate_sprite_link(result)
                image = self.generate_image_link(result)
                embed = self.generate_embed(ctx, sprite, image, result)
                await ctx.send(embed=embed)
        elif len(results) == 0:
            await ctx.send(f"Pokemon `{input}` doesn't exist")
        else:
            sprite = self.generate_sprite_link(results[0])
            image = self.generate_image_link(results[0])
            embed = self.generate_embed(ctx, sprite, image, results[0])
            await ctx.send(embed=embed)
        # await ctx.send(embed=self.post_images())

    def get_pokemon_info(self, input):
        db = mysql()
        query = """
            SELECT
                pkmn.dex AS 'dex',
                name.english AS 'name',
                category.english AS 'category',
                pkmn.type AS 'type',
                pkmn.isotope AS 'isotope',
                pkmn.filename AS 'filename',
                form.name AS 'form',
                pkmn.shiny AS 'shiny'
            FROM pokemon pkmn
            LEFT JOIN pokemon_names name on name.dex = pkmn.dex
            LEFT JOIN pokemon_categories category on category.dex = pkmn.dex
            LEFT JOIN pokemon_form_names form on form.dex = pkmn.dex AND form.type = pkmn.type
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

    def generate_image_link(self, result, shiny=False):
        # Base url for the repo, plus an image cacher link, if we are using it
        base_url = "https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Images/Pokemon/"

        url = ""
        url += base_url
        url += "pokemon_icon_"

        # Checks if a unique file name exists for the Pokemon
        if result['filename'] is None:  # If no specific file name is given
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

    def generate_sprite_link(self, result, shiny=False):
        # Base url for the repo, plus an image cacher link so that the sprite
        # is cropped and looks proper
        base_url = "https://raw.githubusercontent.com/msikma/pokesprite/master/pokemon-gen8/"
        cache_link = "https://images.weserv.nl/?trim=10&url="

        url = ""
        url += base_url

        # If it's shiny, add in that little bit
        if shiny:
            url += "shiny/"
        else:
            url += "regular/"

        # If there is a name there, use it. Otherwise just replace it with an
        # unknown picture
        if result['name']:
            name = result['name'].lower()
            name = name.replace(".", "")
            name = name.replace(" ", "-")
            url += name
        else:
            url = base_url + "unknown-gen5"

        # Finally, add in the file extension
        url += ".png"

        return cache_link + url

    def generate_embed(self, ctx, sprite, image, result):
        # Cherubi green: 0x2FA439
        # Cherubi pink: 0xE66479
        fields = []

        fields.append(["__Category__", result['category'] or u"\u200B", False])
        fields.append(["__Shiny Exists?__", bool(result['shiny']), False])
        fields.append(["__Type__", result['type'] or u"\u200B", True])
        fields.append(["__Isotope__", result['isotope'] or u"\u200B", True])
        fields.append(["__Filename__", result['filename'] or u"\u200B", True])
        fields.append(["__Form Name__", result['form'] or u"\u200B", True])

        embed = lib.embedder.make_embed(
            colour=0x2FA439,
            title="Shiny Checker",
            header=f"{result['name']}",
            content=f"National Dex #{str(result['dex']).zfill(3)}",
            icon=sprite,
            fields=fields,
            thumbnail=image,
            footer=f"Generated by {ctx.author.display_name}"
        )

        return embed


def setup(client):
    client.add_cog(FancyEmbed(client))
