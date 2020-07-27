from discord.ext import commands
from lib.mysql import mysql
import discord
import os

class Preferences(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(Preferences(client))
