from discord.ext import commands
import discord
import random


class Example(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.greetings = [
            "'Ello, gov'nor",
            "Ahoy",
            "Ehh",
            "Hello stranger",
            "Hello",
            "Hey",
            "Hi diddly ho neighbourino",
            "Hi",
            "Hi-ya",
            "Hiya!",
            "Howdy diddly neighborino",
            "Howdy diddly",
            "Howdy",
            "Howdy-do",
            "Shalom",
            "Why hello there",
            "Yo!",
        ]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.client.user.mentioned_in(message):
            return

        content = message.content.replace(f"<@!{self.client.user.id}>", "")
        content = content.strip()

        if message.content in ["hi", "hello", "hey", "yo"]:
            return

        if content.upper() in (name.upper() for name in self.greetings):
            channel = self.client.get_channel(message.channel.id)
            await channel.send(random.choice(self.greetings))
            return

    @commands.command(
        aliases=["hi", "hey", "hiya", "yo"],
        hidden=True
    )
    async def hello(self, ctx):
        await ctx.send(random.choice(self.greetings))


def setup(client):
    client.add_cog(Example(client))
