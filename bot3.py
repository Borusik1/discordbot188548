from unicodedata import category
import random
from aiohttp import request
import interactions
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
from interactions.ext.persistence import PersistentCustomID
from interactions.ext.wait_for import setup


#os.environ['DATABASE_URL'] = 'postgres://etdqcmbnqseqpe:21406b78e6a94b332e1d790b5246565f1144098fd1a95e4fd4d1d8fd4e0ccc07@ec2-54-194-211-183.eu-west-1.compute.amazonaws.com:5432/d3bkqd4pplu1ba'
#os.environ['BOT_TOKEN'] = 'OTE3MDMwMjM4NTk1MjA3MTY4.Yayw9g.1rYs1KWblY90oTXxwGXPlsTXdOQ'
#os.environ['CLIENT_ID'] = 'c9k3wEk8beWmOkiKJ3x0FA'
#os.environ['CLIENT_SECRET'] = '2XFJF6Ue6jIdO17hlVvcAdsj4ycKjA'
#basicConfig(level=DEBUG)


reddit = asyncpraw.Reddit(
	client_id=os.environ["CLIENT_ID"],
	client_secret=os.environ["CLIENT_SECRET"],
	user_agent='random_reddit_bot/0.0.1'
)
bot = interactions.Client(os.environ["BOT_TOKEN"], intents = interactions.Intents.ALL)
connection = psycopg2.connect(os.environ['DATABASE_URL'], sslmode="require")
cursor = connection.cursor()
bot.load("interactions.ext.persistence", cipher_key = "9BB640B714D665C05DE33831EA8E7D5B")
setup(bot)

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
#cursor.execute("DROP TABLE items")
cursor.execute("DROP TABLE message_response")
#for row in cursor.execute("SELECT * FROM role"):
#	print(row)
#connection.commit()

#cursor.execute("""CREATE TABLE IF NOT EXISTS items (
#	name TEXT,
#	id INT,
#	fs BOOL,
#	price INT,
#	usable BOOL,
#	arg numeric(20),
#	guild numeric(20)
#)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS message_response (
	id INT,
	time INT,
	step INT,
	status BOOL,
	values varchar(10000),
	author numeric(20),
	channel numeric(20),
	guild numeric(20),
	message numeric(20)
)""")
connection.commit()

bot.start()
