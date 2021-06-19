from discord.ext import commands
from dotenv import load_dotenv
from lib.mysqlwrapper import mysql
from lib.logger import Logger
from pathlib import Path
import discord
import logging
import os

# Load up the environment variables
env_file_name = '.env'
env_path = Path('.') / env_file_name
load_dotenv(dotenv_path=env_path)

# Check if .env.local exists, if so, load up those variables, overriding the
# previously set ones
local_env_file_name = env_file_name + '.local'
local_env_path = Path('.') / local_env_file_name
if os.path.isfile(local_env_file_name):
    load_dotenv(dotenv_path=local_env_path, override=True)

# Set up loggers
Logger("cogs")
Logger("discord")
Logger("lib", "debug")
Logger("mysql", None, "file")  # MySQL is first, since it's one of the first things called
Logger("main")
logger = logging.getLogger("main")


# Sets the guild preferences for the guilds
def set_default_preferences(db, guild_id):
    query = """
        INSERT IGNORE INTO guild_preferences (guild, command_prefix)
        VALUES (%s, %s);
    """
    db.execute(query, [guild_id, os.environ['COMMAND_PREFIX']])


# Set the prefixes for each of the guilds in to a global variable
prefixes = {}


# This is used for the command_prefix for starting up the bot. It gets run
# against any message that the bot can see to check if it was a command or not.
def get_prefix(client, message):
    # If it is a DM from a user, use these. "" needs to be on the very end of
    # the previous prefixes won't work.
    if isinstance(message.channel, discord.DMChannel):
        return ("!", ".", "?", "$", "%", ":", ";", ">", "")

    # Link the prefixes variable in this function to the global one, so it
    # all updates
    global prefixes

    # If their prefix isn't in the list for some reason, re-run
    if message.guild.id not in prefixes:
        db = mysql()
        query = """
            SELECT
                guild,
                command_prefix

            FROM guild_preferences;
        """
        prefix_list = db.query(query)
        db.close()
        for prefix in prefix_list:
            prefixes[prefix['guild']] = prefix['command_prefix']

    # Return their prefix from the prefixes dictionary
    return commands.when_mentioned_or(*prefixes[message.guild.id])(client, message)


def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)


# Set up intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

# Start up the bot
client = commands.Bot(
    command_prefix=get_prefix,
    description="Cherubi Bot for Pokemon Go Servers",
    owner_id=int(os.environ['BOT_AUTHOR']),
    status=discord.Status.dnd,
    intents=intents
)


@client.event
async def on_ready():
    status = client.get_cog('Status')
    if os.environ['DEBUG'].lower() == "true":
        await status.set_status("idle")
        await status.set_activity("playing around in debug mode.")

    else:
        await status.set_status("online")
        await status.set_activity(f"listening your input. Helping ~{len(client.guilds)} servers and ~{len(client.users)} users.")

    logger.info("Bot is ready.")


@client.event
async def on_command_error(ctx, exc):
    IGNORE_EXCEPTIONS = (commands.CommandNotFound, commands.BadArgument)
    if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
        pass

    elif isinstance(exc, commands.MissingRequiredArgument):
        await ctx.send("One or more required arguments are missing.")
        await ctx.send_help(str(ctx.command))

    elif isinstance(exc, commands.CommandOnCooldown):
        await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")

    elif isinstance(exc, commands.errors.CheckFailure):
        await ctx.send("You don't have permission to use that command")

    elif hasattr(exc, "original"):
        # if isinstance(exc.original, HTTPException):
        #   await ctx.send("Unable to send message.")

        if isinstance(exc.original, discord.errors.Forbidden):
            await ctx.send("I do not have permission to do that.")

        else:
            raise exc.original

    else:
        raise exc


@client.event
async def on_guild_join(guild):
    logger.info(f"Joined guild: {guild.id} / {guild.name}")
    # Set the default preferences for a guild upon joining
    db = mysql()
    set_default_preferences(db, guild.id)
    db.close()


@client.event
async def on_guild_remove(guild):
    logger.info(f"Left guild: {guild.id} / {guild.name}")

    # Removes the preferences line for a guild
    db = mysql()
    query = """
        DELETE FROM guild_preferences
        WHERE guild = %s;
    """
    db.execute(query, [guild.id])
    db.close()


@client.event
async def on_connect():
    db = mysql()

    # Whenever the bot connects up to Discord double check that at least the
    # default preferences are set for each guild it is in
    for guild in client.guilds:
        set_default_preferences(db, guild.id)

    db.close()

    logger.info("Bot Connected")


@client.event
async def on_disconnect():
    logger.info("Bot Disconnected")


@client.command(
    brief="PONG!"
)
@commands.cooldown(1, 10, commands.BucketType.guild)
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")


@client.command()
@commands.guild_only()
@commands.check_any(commands.is_owner(), is_guild_owner())
async def changeprefix(ctx, prefix):
    # If someone tries to set more than a single character
    if len(prefix) > 1:
        ctx.send("Command prefix can only be a single character")
        return

    # Store the character in the preferences table
    db = mysql()
    query = """
        UPDATE guild_preferences
        SET command_prefix = %s
        WHERE guild = %s;
    """
    db.execute(query, [prefix, ctx.guild.id])
    db.close()

    # Set the local prefix dictionary to blank
    global prefixes
    prefixes = {}

    # Then finally send the user a message saying that it is changed
    await ctx.send(f"Prefix has been changed to: {prefix}")


@client.command()
@commands.is_owner()
async def load(ctx, extension):
    logger.info(f"Loading {extension}")
    await ctx.send(f"Loading {extension}")
    client.load_extension(f"cogs.{extension}")


@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    logger.info(f"Unloading {extension}")
    await ctx.send(f"Unloading {extension}")
    client.unload_extension(f"cogs.{extension}")


@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    logger.info(f"Reloading {extension}")
    await ctx.send(f"Reloading {extension}")
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")

# Debug commands meant for when working on the bot
if os.environ['DEBUG'].lower() == "true":
    @client.command()
    @commands.dm_only()
    @commands.is_owner()
    async def stop(ctx):
        await ctx.send("Stopping...")
        logger.critical("`stop` command was run. Stopping...")
        await client.close()

# Load up the cogs
for filename in os.listdir("./bot/cogs"):
    if filename.endswith(".py"):
        try:
            client.load_extension(f"cogs.{filename[:-3]}")
        except Exception:
            logger.critical(f"Unable to load {filename} cog.", exc_info=1)
            raise SystemExit

client.run(os.environ['DISCORD_BOT_TOKEN'])
