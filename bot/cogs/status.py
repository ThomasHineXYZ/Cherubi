from discord.ext import commands
import discord
import os

class Status(commands.Cog):
    def __init__(self, client):
        self.client = client

        self._message = "playing Booting up..."
        self._status = "online"

    @property
    def message(self):
        return self._message.format(users=len(self.client.users), guilds=len(self.client.guilds))

    @property
    def status(self):
        return self._message.format(users=len(self.client.users), guilds=len(self.client.guilds))

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type.")

        self._message = value

    @status.setter
    def status(self, value):
        if value not in ("online", "offline", "idle", "dnd", "do_not_disturb",
            "invisible"):
            raise ValueError("Invalid status type.")

        self._status = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.client.change_presence(
            activity=discord.Activity(
                name=_name,
                type=getattr(discord.ActivityType, _type)
            ),
            status=getattr(discord.Status, self._status)
        )

    async def set_activity(self, text: str):
        self.message = text
        await self.set()

    async def set_status(self, text: str):
        self.status = text
        await self.set()

def setup(client):
    client.add_cog(Status(client))
