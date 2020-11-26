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
            "Bonjour",
            "Ciao",
            "Ehhhh",
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
            "alright, mate?",
            "evening",
            "good afternoon",
            "good evening",
            "good morning",
            "good night",
            "greetings"
            "greets",
            "guten tag",
            "guten tog",
            "gutentag",
            "gutentog",
            "hallo",
            "hay",
            "hays",
            "heys"
            "how are you doing",
            "how you doing",
            "kei halla",
            "knee how",
            "morning",
            "nee how",
            "nei how",
            "night",
            "ola",
            "top of the morning to ya",
            "top of the morning to you",
            "wassup",
            "whats good",
            "wuzzup",
            "👋",
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
        saying = "hey"  # Heyyyyy
        saying2 = "hay"  # Hayyyyyy
        saying3 = "hel"  # Hellllllllo
        saying4 = "he"  # Heeeeeeeeey
        for _ in range(20):
            # Heyyyyy
            saying += "y"
            self.greeting_watch.append(saying)

            # Hayyyyyy
            saying2 += "y"
            self.greeting_watch.append(saying2)

            # Hellllllllo
            saying3 += "l"
            self.greeting_watch.append(f"{saying3}o")

            # Heeeeeeeeey
            saying4 += "e"
            self.greeting_watch.append(f"{saying4}y")

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

    @commands.command(
        name="b",
        brief="B Button Translator",
        description="Cherubi Bot - Fun Stuff",
        help="Turn either the previous message, or the given string, in to a B Button Emoji message.",
    )
    async def b_button_translator(self, ctx, *, input_message=""):
        # This is just to allow it to be changed easily
        # It's the red B emoji
        b_emoji = "🅱️"

        # Get the message. Either the previous one or the one that was passed
        # to this
        message = ""
        if input_message:
            message = input_message
        else:
            channel = self.client.get_channel(ctx.channel.id)
            last_message = await channel.history(limit=2).flatten()
            message = last_message[1].content

        # Split the message by spaces, so we get a list of words
        message_split = message.split(" ")

        # These are just some exception words that have a special replacement
        exception_words = {
            "potato": f"{b_emoji}o{b_emoji}ato",
            "potatoes": f"{b_emoji}o{b_emoji}atoes",
        }

        # For each word in the message, if it's not an exception word, replace
        # the first character of it with the b emoji
        new_message = ""
        for word in message_split:
            new_word = ""
            # If it's less than two characters, just in case, just skip the
            # word and add it back
            if len(word) < 2:
                new_word = word
            elif word.lower() in exception_words:
                new_word = exception_words[word.lower()]
            else:
                new_word = b_emoji + word[1:]

            # Add the new word together with the previous ones, and add a space
            # so it formats nicely
            new_message += new_word + " "

        # Strip out any leading or trailing whitespace
        new_message = new_message.strip()

        # aaaaaaand send it!
        await ctx.send(new_message)

    @commands.command(
        name="emoji",
        brief="Emoji Translator",
        description="Cherubi Bot - Fun Stuff",
        help="Turn either the previous message, or the given string, in to a just emoji characters.",
    )
    async def emoji_translator(self, ctx, *, input_message=""):
        # Dictionary of all of the letter emojis
        letters = {
            "a": "🇦",
            "b": "🇧",
            "c": "🇨",
            "d": "🇩",
            "e": "🇪",
            "f": "🇫",
            "g": "🇬",
            "h": "🇭",
            "i": "🇮",
            "j": "🇯",
            "k": "🇰",
            "l": "🇱",
            "m": "🇲",
            "n": "🇳",
            "o": "🇴",
            "p": "🇵",
            "q": "🇶",
            "r": "🇷",
            "s": "🇸",
            "t": "🇹",
            "u": "🇺",
            "v": "🇻",
            "w": "🇼",
            "x": "🇽",
            "y": "🇾",
            "z": "🇿",
        }

        # Get the message. Either the previous one or the one that was passed
        # to this
        message = ""
        if input_message:
            message = input_message
        else:
            channel = self.client.get_channel(ctx.channel.id)
            last_message = await channel.history(limit=2).flatten()
            message = last_message[1].content

        # Split the message by spaces, so we get a list of words
        message_split = message.split(" ")

        # Replace all of the letters in a word with their emoji version
        new_message = ""
        for word in message_split:
            new_word = ""
            for letter in word:
                if letter.lower() in letters:
                    # Put a space between them, otherwise they mess up in
                    # Discord
                    new_word += letters[letter.lower()] + " "
                else:
                    new_word += letter

            # Remove any extra whitespace around the word, then add in a tab
            # character so there is some spacing between words
            new_word = new_word.strip()
            new_message += new_word + u"\u0009"

            # If the message is over 200 characters, then send what we have so
            # far prematurely so it doesn't get cut off. Then empty out the
            if len(new_message) > 256:
                new_message = new_message.strip()
                await ctx.send(new_message)
                new_message = ""

        # Strip out any leading or trailing whitespace
        new_message = new_message.strip()

        # If there is anything left to send, then send it
        if new_message:
            await ctx.send(new_message)

    @commands.command(
        name="f",
        brief="Pay your respects",
        description="Cherubi Bot - Fun Stuff",
        help="Pay your respects by putting an \"f\" in chat.",
    )
    async def pay_respects(self, ctx):
        await ctx.send(f"{ctx.author.display_name} has paid their respects.")


def setup(client):
    client.add_cog(Fun(client))
