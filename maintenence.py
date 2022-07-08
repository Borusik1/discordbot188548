import discord
from discord.ext import commands
from discord.ui import Button
import json
import sqlite3
from tabulate import tabulate
from config import settings
import asyncio
from itertools import cycle



client = commands.Bot(command_prefix = settings['PREFIX'], intents = discord.Intents.all())
client.remove_command("help")
connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
	print("Bot Has been runned")
	msg = cycle(status)
	while not client.is_closed():
		next_status= next(msg)
		await client.change_presence(activity = discord.Game(name=next_status))
		await asyncio.sleep(1)

status=['Модернизирует свой код', "Подождите.", "Подождите..", "Подождите..."]



client.run(settings['TOKEN'])
