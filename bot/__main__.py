from discord.ext import commands
from dotenv import load_dotenv
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

# Start up the bot
client = commands.Bot(command_prefix = os.environ['COMMAND_PREFIX'])

@client.event
async def on_ready():
    status = client.get_cog('Status')
    if os.environ['DEBUG'].lower() == 'true':
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

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

# Debug commands meant for when working on the bot
if os.environ['DEBUG'].lower() == 'true':
    @client.command()
    async def load(ctx, extension):
        print(f'Loading {extension}')
        await ctx.send(f'Loading {extension}')
        client.load_extension(f'cogs.{extension}')

    @client.command()
    async def unload(ctx, extension):
        print(f'Unloading {extension}')
        await ctx.send(f'Unloading {extension}')
        client.unload_extension(f'cogs.{extension}')

    @client.command()
    async def reload(ctx, extension):
        print(f'Reloading {extension}')
        await ctx.send(f'Reloading {extension}')
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')

for filename in os.listdir('./bot/cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}');

client.run(os.environ['DISCORD_BOT_TOKEN'])
