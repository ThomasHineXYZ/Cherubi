from discord.ext import commands, tasks
import discord
import random
import re


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

        print("Loading fun cog")
        self.greetings = [
            "'Ello, gov'nor",
            "A pleasure meet you",
            "Ahoy",
            "Aloha",
            "Alright, mate?",
            "Bonjour",
            "Ciao",
            "Ehh",
            "G'day",
            "G'day, mate!",
            "Goodmorrow!",
            "Greetings and salutations.",
            "Hallo",
            "Hello stranger",
            "Hello",
            "Hello, my name is Inigo Montoya",
            "Here's Johnny!",
            "Hey",
            "Heyo",
            "Hi diddly ho neighbourino",
            "Hi",
            "Hi-ya",
            "Hiya!",
            "Holla",
            "Hola",
            "How do you do?",
            "How you doin'?",
            "Howdy diddly neighborino",
            "Howdy diddly",
            "Howdy",
            "Howdy-do",
            "Konnichiwa",
            "Lovely to see you.",
            "Namaste",
            "Nice to meet you",
            "Que pasa",
            "Salute plurimam dicit",
            "Shalom",
            "Sup, Homeslice?",
            "Sup?",
            "What's crackin?",
            "What's happening?",
            "What's new?",
            "What's the craic?",
            "What's up?",
            "Why hello there",
            "Yo!",
        ]
        self.add_special_greetings.start()

    def cog_unload(self):
        print("Unloading fun cog")

    @tasks.loop(count=1)
    async def add_special_greetings(self):
        """Adds in special greetings when the bot is online

        This allows for adding greetings that require the bot to tag its own
        ID or any other information it needs when it is ready and connected to
        Discord
        """
        # Wait for the bot to be connected and ready otherwise this will fail
        await self.client.wait_until_ready()

        # This adds in a Doctor Who reference. "Doctor? Doctor who?"
        self.greetings.append(
            f"<@!{self.client.user.id}>, <@!{self.client.user.id}> who?"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listens for any messages and sees if someone is saying hi to the bot

        This does various checks to make sure that someone is trying to say hi
        to the bot. If it passes them all it chooses randomly from the list of
        greetings above and sends them to the channel that the user wrote the
        tagged message in.
        """
        # Ignore the message if the bot isn't tagged at all
        if not self.client.user.mentioned_in(message):
            return

        # If multiple "people" were mentioned, just ignore it outright
        if len(message.mentions) > 1:
            return

        # Remove the tagged bit
        content = message.content.replace(f"<@!{self.client.user.id}>", "")
        content = content.strip()

        # Double checks for if the user wrote the hello command, if so just
        # return
        if (message.content.startswith(f"<@!{self.client.user.id}>")
            and content == "hello"):
            return

        # Double checks for if the user wrote the any of the hello command
        # aliases, if so just return
        aliases = self.client.get_command("hello").aliases
        if (message.content.startswith(f"<@!{self.client.user.id}>")
            and content in aliases):
            return

        # Remove any special characters
        content = re.sub(r"[^a-zA-Z0-9]", "", content)
        content = content.strip()

        # Checks if the message has any of the greetings from above in it,
        # if so, then assume the person is trying to say hi and send the random
        # greeting to the channel that the message was sent from.
        if content.upper() in (name.upper() for name in self.greetings):
            channel = self.client.get_channel(message.channel.id)
            await channel.send(random.choice(self.greetings))
            return

    @commands.command(
        name="hello",
        aliases=["hi", "hey", "hiya", "yo"],
        hidden=True
    )
    async def greetings_command(self, ctx):
        await ctx.send(random.choice(self.greetings))


def setup(client):
    client.add_cog(Fun(client))
