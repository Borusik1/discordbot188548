import interactions
import json
from tabulate import tabulate
from config import settings
import asyncio
from itertools import cycle
import datetime
import re
import psycopg2
import calendar, time

bot = interactions.Client("OTE3MDMwMjM4NTk1MjA3MTY4.Yayw9g.1rYs1KWblY90oTXxwGXPlsTXdOQ")
connection = psycopg2.connect(settings["DB_URI"], sslmode="require")
cursor = connection.cursor()



cursor.execute("""CREATE TABLE IF NOT EXISTS users (
	id numeric(20),
	cash integer,
	rep integer,
	guild numeric(20)
	)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS status (
	id int,
	status BOOL,
	arg numeric(20),
	guild numeric(20)
	)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS counter (
	stat BOOL,
	author numeric(20),
	channel numeric(20),
	guild numeric(20)
	)""")

#cursor.execute("DROP TABLE status")
#cursor.execute("DROP TABLE counter")
#cursor.execute("DROP TABLE users")
#for row in cursor.execute("SELECT * FROM role"):
#	print(row)

@bot.command(
	name ="hello",
	description="Hello",
	options=[
		interactions.Option(
			type=interactions.OptionType.STRING,
			name="message",
			description="send"
			)
	])
async def hello(ctx, message: str):
	await ctx.send(message)


bot.start()