from unicodedata import category
import random
from aiohttp import request
import interactions
from interactions.ext.get import get
from interactions.ext.enhanced import cooldown
from interactions.ext.checks import is_owner, guild_only
import json
from tabulate import tabulate
import asyncio
from itertools import cycle
import datetime
import re
import psycopg2
import calendar, time
import os
from logging import basicConfig, DEBUG
import asyncpraw


os.environ['DATABASE_URL'] = 'postgres://etdqcmbnqseqpe:21406b78e6a94b332e1d790b5246565f1144098fd1a95e4fd4d1d8fd4e0ccc07@ec2-54-194-211-183.eu-west-1.compute.amazonaws.com:5432/d3bkqd4pplu1ba'
os.environ['BOT_TOKEN'] = 'OTE3MDMwMjM4NTk1MjA3MTY4.Yayw9g.1rYs1KWblY90oTXxwGXPlsTXdOQ'
os.environ['CLIENT_ID'] = 'c9k3wEk8beWmOkiKJ3x0FA'
os.environ['CLIENT_SECRET'] = '2XFJF6Ue6jIdO17hlVvcAdsj4ycKjA'
#basicConfig(level=DEBUG)


reddit = asyncpraw.Reddit(
	client_id=os.environ["CLIENT_ID"],
	client_secret=os.environ["CLIENT_SECRET"],
	user_agent='random_reddit_bot/0.0.1'
)
bot = interactions.Client(os.environ["BOT_TOKEN"], intents = interactions.Intents.ALL)
connection = psycopg2.connect(os.environ['DATABASE_URL'], sslmode="require")
cursor = connection.cursor()

cogs = []
for filename in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs")):
	if filename.endswith(".py"):
		cogs.append(filename.replace(".py", ""))
for cog in cogs:
	bot.load("cogs." + cog, connection=connection, cursor=cursor, reddit=reddit)
print("Cogs loaded")

#cursor.execute("DROP TABLE status")
#cursor.execute("DROP TABLE counter")
#cursor.execute("DROP TABLE users")
#for row in cursor.execute("SELECT * FROM role"):
#	print(row)



@bot.command(
	name="balance",
	description="Посмотреть баланс",
	options=[
		interactions.Option(
			name="user",
			description="Участник которого желаете посмотреть баланс",
			type=interactions.OptionType.USER,
			required=False,
		),
	],
)
@guild_only()
async def balance(ctx, user = None):
	pass




bot.start()