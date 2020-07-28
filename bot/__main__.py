from discord.ext import commands
from dotenv import load_dotenv
from lib.mysql import mysql
from pathlib import Path
import discord
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

# Sets the guild preferences for the guilds
def set_default_preferences(guild_id):
    db = mysql()
    query = """
        INSERT INTO preferences (guild, command_prefix)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE guild = guild;
    """
    db.execute(query, [guild_id, os.environ['COMMAND_PREFIX']])
    db.close()

# Set the prefixes for each of the guilds
prefixes = {}
def get_prefix(client, message):
    # If their prefix isn't in the list for some reason, re-run
    global prefixes
    if message.guild.id not in prefixes:
        set_default_preferences(message.guild.id)
        db = mysql()
        query = """
            SELECT
                guild,
                command_prefix

            FROM preferences;
        """
        prefix_list = db.query(query)
        db.close()
        for guild, prefix in prefix_list:
            prefixes[guild] = prefix

    # If the guild still isn't in the prefixes list, throw an error
    if message.guild.id not in prefixes:
        raise ValueError(f"{message.guild.id} doesn't have an entry in the preferences table")

    # Return their prefix from the prefixes dictionary
    return prefixes[message.guild.id]

# Start up the bot
client = commands.Bot(command_prefix = get_prefix)

@client.event
async def on_ready():
    status = client.get_cog('Status')
    if os.environ['DEBUG'].lower() == "true":
        await status.set_status("idle")
        await status.set_activity("playing around in debug mode.")

    else:
        await status.set_status("online")
        await status.set_activity("listening your input.")

    print("Bot is ready.")

@client.event
async def on_command_error(ctx, exc):
    IGNORE_EXCEPTIONS = (commands.CommandNotFound, commands.BadArgument)
    if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
        pass

    elif isinstance(exc, commands.MissingRequiredArgument):
        await ctx.send("One or more required arguments are missing.")

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
    print(f"Joined guild: {guild.id} / {guild.name}")

    # Set the default preferences for a guild upon joining
    set_default_preferences(guild.id)

@client.event
async def on_guild_remove(guild):
    print(f"Left guild: {guild.id} / {guild.name}")

    # Removes the preferences line for a guild
    db = mysql()
    query = """
        DELETE FROM preferences
        WHERE guild = %s;
    """
    db.execute(query, [guild.id])
    db.close()

@client.command()
@commands.cooldown(1, 10, commands.BucketType.guild)
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@client.command()
@commands.is_owner()
async def changeprefix(ctx, prefix):
    # If someone tries to set more than a single character
    if len(prefix) > 1:
        ctx.send("Command prefix can only be a single character")
        return

    # Store the character in the preferences table
    db = mysql()
    query = """
        UPDATE preferences
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

# Debug commands meant for when working on the bot
if os.environ['DEBUG'].lower() == "true":
    @client.command()
    async def load(ctx, extension):
        print(f"Loading {extension}")
        await ctx.send(f"Loading {extension}")
        client.load_extension(f"cogs.{extension}")

    @client.command()
    async def unload(ctx, extension):
        print(f"Unloading {extension}")
        await ctx.send(f"Unloading {extension}")
        client.unload_extension(f"cogs.{extension}")

    @client.command()
    async def reload(ctx, extension):
        print(f"Reloading {extension}")
        await ctx.send(f"Reloading {extension}")
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")

# Load up the cogs
for filename in os.listdir("./bot/cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}");

client.run(os.environ['DISCORD_BOT_TOKEN'])
