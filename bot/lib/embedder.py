import discord
from datetime import datetime

emoji_letters = {
    "A": "🇦",
    "B": "🇧",
    "C": "🇨",
    "D": "🇩",
    "E": "🇪",
    "F": "🇫",
    "G": "🇬",
    "H": "🇭",
    "I": "🇮",
    "J": "🇯",
    "K": "🇰",
    "L": "🇱",
    "M": "🇲",
    "N": "🇳",
    "O": "🇴",
    "P": "🇵",
    "Q": "🇶",
    "R": "🇷",
    "S": "🇸",
    "T": "🇹",
    "U": "🇺",
    "V": "🇻",
    "W": "🇼",
    "X": "🇽",
    "Y": "🇾",
    "Z": "🇿",
    "arrow-back": "◀️",
    "arrow-forward": "▶️",
    "arrow-previous": "⏪",
    "arrow-next": "⏩",
    "arrow-first": "⏮️",
    "arrow-last": "⏭️",
}

colours = {
    "blue": discord.Colour.blue(),
    "blurple": discord.Colour.blurple(),
    "dark_blue": discord.Colour.dark_blue(),
    "dark_gold": discord.Colour.dark_gold(),
    "dark_green": discord.Colour.dark_green(),
    "dark_grey": discord.Colour.dark_grey(),
    "dark_magenta": discord.Colour.dark_magenta(),
    "dark_orange": discord.Colour.dark_orange(),
    "dark_purple": discord.Colour.dark_purple(),
    "dark_red": discord.Colour.dark_red(),
    "dark_teal": discord.Colour.dark_teal(),
    "darker_grey": discord.Colour.darker_grey(),
    "gold": discord.Colour.gold(),
    "green": discord.Colour.green(),
    "greyple": discord.Colour.greyple(),
    "light_grey": discord.Colour.light_grey(),
    "lighter_grey": discord.Colour.lighter_grey(),
    "magenta": discord.Colour.magenta(),
    "orange": discord.Colour.orange(),
    "purple": discord.Colour.purple(),
    "red": discord.Colour.red(),
    "teal": discord.Colour.teal(),
}

def make_embed(
    colour = None,
    content = None,
    fields = None,
    footer = None,
    footer_icon = None,
    header = None,
    icon = None,
    image = '',
    thumbnail = '',
    title_name = None,
    title_url = None,
    type = ''
):
    type_icon_hosting = "https://raw.githubusercontent.com/guitaristtom/shiny-bot/master/bot/assets/icons"
    types = {
        'error':{
            'icon':f'{type_icon_hosting}/error.png',
            'colour':'red'
        },
        'warning':{
            'icon':f'{type_icon_hosting}/warning.png',
            'colour':'gold'
        },
        'info':{
            'icon':f'{type_icon_hosting}/information.png',
            'colour':'blurple'
        },
        'success':{
            'icon':f'{type_icon_hosting}/success.png',
            'colour':'green'
        },
        'help':{
            'icon':f'{type_icon_hosting}/help.png',
            'colour':'blue'
        }
    }

    # If the type is given, but no colour override, then use that colour
    if not colour and type and type in types.keys():
        colour = types[type]['colour']

    # If the given colour is in the colour table, then use it
    if colour in colours.keys():
        embed_colour = colours[colour]
    else:
        # Otherwise set the colour as Cherubi green
        # Cherubi green: 0x2FA439
        # Cherubi pink: 0xE66479
        embed_colour = 0x2FA439

    # Set the icon. If no specific icon is given, use the type, if that doesn't
    # work then give the Discord Empty Object to stop errors
    if icon:
        embed_icon = icon
    elif type and type in types.keys():
        print(f"Type {types[type]['icon']} chosen")
        embed_icon = types[type]['icon']
    else:
        embed_icon = discord.Embed.Empty

    # If no title URL is given, then we have to give the Discord Embed Empty
    # object
    if not title_url:
        title_url = discord.Embed.Empty

    embed = discord.Embed(
        description=content,
        title = header,
        colour = embed_colour,
        timestamp = datetime.utcnow()
    )

    embed.set_author(name=title_name, icon_url=embed_icon, url=title_url)

    # If a thumbnail or main image URL is given, show it!
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)

    # If fields are given, iterate through them and add them
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    # If footer information is given, set it
    if footer or footer_icon:
        footer = {'text': footer}
        if footer_icon:
            footer['icon_url'] = footer_icon
        embed.set_footer(**footer)

    return embed
