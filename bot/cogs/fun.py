from collections import OrderedDict
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
            "Salutations",
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
        self.greeting_watch = [
            "afternoon",
            "evening",
            "greetings"
            "greets",
            "hallo",
            "hay",
            "hays",
            "heys"
            "how are you doing",
            "how you doing",
            "morning",
            "wassup",
            "whats good",
            "wuzzup",
        ]
        self.add_more_greeting_stuff.start()

    def cog_unload(self):
        print("Unloading fun cog")

    @tasks.loop(count=1)
    async def add_more_greeting_stuff(self):
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

        # Set up the greeting watch list
        for greeting in self.greetings:
            value = greeting.lower()

            # Add in all of the (lowered) greetings in to the greeting_watch
            # list
            self.greeting_watch.append(value)

            # Also strip any non-stadnard values from it
            value = re.sub(r"[^a-zA-Z0-9\-_]", "", value)
            self.greeting_watch.append(value)

        # Add several different hey variants to the watch list
        saying = "hey"
        saying2 = "hay"
        for _ in range(20):
            saying += "y"
            self.greeting_watch.append(saying)

            saying2 += "y"
            self.greeting_watch.append(saying2)

        # Remove duplicates to save a tiny bit more memory
        self.greeting_watch = list(OrderedDict.fromkeys(self.greeting_watch))

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
        if content.lower() in (greeting for greeting in self.greeting_watch):
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
