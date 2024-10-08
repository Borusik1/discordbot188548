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
