from discord.ext import commands
import discord
import lib.embedder


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Checks for `!help`

        Checks if anyone put `!help` in a message in a guild, if so then give
        them a little reminder that the bots help command is actually on a
        different prefix (if it is)
        """
        # If this isn't a text channel in a guild, then skip it
        if not isinstance(message.channel, discord.TextChannel):
            return

        # If the message wasn't !help, then skip it
        if message.content != "!help":
            return

        # Check if the guild's prefix is !, is so then skip it
        guild_prefix = await self.client.get_prefix(message)
        if guild_prefix[2] == "!":
            return

        # If it made it this far, then give it an embed saying what the bots
        # actual help command is
        channel = self.client.get_channel(message.channel.id)
        await channel.send(embed=lib.embedder.make_embed(
            type="help",
            title="Would you like some help?",
            content=f"For help with me, go `{guild_prefix[2]}help`, tag me \
and put help, or DM me and ask me for help.",
        ))


def setup(client):
    client.add_cog(Help(client))

