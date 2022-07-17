from unicodedata import category
import random
from aiohttp import request
import interactions
from interactions.ext.get import get
from interactions.ext.enhanced import cooldown
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

#os.environ['DATABASE_URL'] = 'postgres://etdqcmbnqseqpe:21406b78e6a94b332e1d790b5246565f1144098fd1a95e4fd4d1d8fd4e0ccc07@ec2-54-194-211-183.eu-west-1.compute.amazonaws.com:5432/d3bkqd4pplu1ba'
#os.environ['BOT_TOKEN'] = 'OTE3MDMwMjM4NTk1MjA3MTY4.Yayw9g.1rYs1KWblY90oTXxwGXPlsTXdOQ'
#os.environ['CLIENT_ID'] = 'c9k3wEk8beWmOkiKJ3x0FA'
#os.environ['CLIENT_SECRET'] = '2XFJF6Ue6jIdO17hlVvcAdsj4ycKjA'
#basicConfig(level=DEBUG)

database = os.environ['DATABASE_URL']
token = os.environ["BOT_TOKEN"]
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
reddit = asyncpraw.Reddit(
	client_id=client_id,
	client_secret=client_secret,
	user_agent='random_reddit_bot/0.0.1'
)
bot = interactions.Client(token, intents = interactions.Intents.ALL)
connection = psycopg2.connect(database, sslmode="require")
cursor = connection.cursor()
imgs = []
subreddits = ['hentai', 'porn', "nsfw", "hentaibondage", "yuri", "YuriHentai"]
subs= []



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

@bot.event
async def on_start():
	await bot.change_presence(interactions.ClientPresence(activities=[interactions.PresenceActivity(name="только slash-commands", type=interactions.PresenceActivityType.GAME)]))
	await asyncio.sleep(2)
	for guild in bot.guilds:
		await asyncio.sleep(2)
		members = await guild.get_all_members()
		for member in members:
			await asyncio.sleep(0.01)
			member1 = int(member.id)
			guild1 = int(guild.id)
			cursor.execute("SELECT id FROM users where id=%s and guild=%s", (member1, guild1))
			if cursor.fetchone()==None:
				cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (member1, 0, 0, guild1))
				connection.commit()
			else:
				pass
	print("Bot Has been runned")
	print(f"Ping: {bot.latency}")
	subred = cycle(subreddits)
	while True:
		next_subred = next(subred)
		await asyncio.sleep(10)
		for guild in bot.guilds:
			guild1 = int(guild.id)
			cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (4, guild1))
			if cursor.fetchone()!=None:
				cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (4, guild1))
				for row in cursor.fetchone():
					nsfw1 = await reddit.subreddit(next_subred)
					if not subs:
						async for nsfw in nsfw1.hot(limit=300):
							subs.append(nsfw)
					rand_nsfw = random.choice(subs)
					if rand_nsfw.is_self:
						pass
					else:
						if rand_nsfw.title not in imgs:
							url = "https://www.reddit.com/"+rand_nsfw.permalink
							channel = await get(bot, interactions.Channel, channel_id=row)
							await channel.set_nsfw(nsfw=True)
							embed = interactions.Embed(title=f"[{rand_nsfw.title}]({url})")
							embed.set_image(url=rand_nsfw.url)
							embed.set_author(name=f"/{next_subred} (hot)")
							await channel.send(embeds=embed)
							imgs.append(rand_nsfw.title)
					nsfw = await reddit.subreddit(next_subred)
					nsfw = nsfw.new(limit=1)
					item = await nsfw.__anext__()
					if item.title not in imgs:
						if item.is_self:
							pass
						else:
							url = "https://www.reddit.com/"+item.permalink
							channel = await get(bot, interactions.Channel, channel_id=row)
							await channel.set_nsfw(nsfw=True)
							embed = interactions.Embed(title=f"[{rand_nsfw.title}]({url})")
							embed.set_image(url=item.url)
							embed.set_author(name=f"/{next_subred} (newest)")
							await channel.send(embeds=embed)
							imgs.append(item.title)
		
		

@bot.event
async def on_guild_member_add(member):
	member1 = int(member.id)
	guild = int(member.guild_id)
	cursor.execute("SELECT id FROM users WHERE id = %s and guild=%s;", (member1, guild))
	if cursor.fetchone()==None:
		cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (member1, 0, 0, guild))
		connection.commit()
	guild1 = member.guild_id
	guild_same = await get(bot, interactions.Guild, guild_id=guild1)
	cursor.execute("SELECT arg, status FROM status where id=%s and guild=%s;", (1, guild))
	for row in cursor.fetchall():
		status = row[1]
		c_id = row[0]
		if status == True:
			channel = await get(bot, interactions.Channel, channel_id=c_id)
			embed=interactions.Embed(color =0x8346f0, description=f"**Добро пожаловать на наш сервер, здесь ты сможешь провести сделки через наших гарантов без какого-либо обмана, а так же завести новых друзей!**")
			await channel.send(f"Привет дружище <@{member.id}>!", embeds=embed)
		else:
			pass

@bot.command(
	name="set",
	description="None",
	default_member_permissions=interactions.Permissions.ADMINISTRATOR,
	options=[
		interactions.Option(
			name="channel",
			description="Установить канал для приветствий",
			type=interactions.OptionType.SUB_COMMAND,
			options=[
				interactions.Option(
					name="channel",
					description="Канал на который установить",
					type=interactions.OptionType.CHANNEL,
					required=True,
				),
			],
		),
		interactions.Option(
			name="category",
			description="Установить категорию для создания тикетов",
			type=interactions.OptionType.SUB_COMMAND,
			options=[
				interactions.Option(
					name="category",
					description="Категория на которую установить",
					type=interactions.OptionType.CHANNEL,
					required=True,
				),

			],
		),
		interactions.Option(
			name="requests",
			description="Установить канал в которой приходят запросы",
			type=interactions.OptionType.SUB_COMMAND,
			options=[
				interactions.Option(
					name="channel",
					description="Канал на который установить",
					type=interactions.OptionType.CHANNEL,
					required=True,
				),

			],
		),
		interactions.Option(
			name="nsfw",
			description="Установить канал для NSFW(18+) рассылки",
			type=interactions.OptionType.SUB_COMMAND,
			options=[
				interactions.Option(
					name="channel",
					description="Канал на который установить",
					type=interactions.OptionType.CHANNEL,
					required=True,
				),

			],
		),
	],
)
async def cmd(ctx, sub_command: str, channel = None, category = None):
	await ctx.defer()
	guild = int(ctx.guild_id)
	if sub_command=="channel":
		channel1 = int(channel.id)
		if channel.type == interactions.ChannelType.GUILD_TEXT:
			cursor.execute("SELECT id FROM status where id=%s and guild=%s", (1, guild))
			if cursor.fetchone()==None:
				cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (1, True, channel1, guild))
			else:
				cursor.execute('UPDATE status SET arg=%s where id=%s and guild=%s', (channel1, 1, guild))
			connection.commit()
			embed=interactions.Embed(color =0x2ecc71, description=f"Приветственный канал успешно настроен на <#{channel1}>")
			await ctx.send(embeds=embed)
		else:
			embed=interactions.Embed(color =0xf50a19, description=f"Это не текстовый канал")
			await ctx.send(embeds=embed)
	elif sub_command=="category":
		if category.type == interactions.ChannelType.GUILD_CATEGORY:
			category1 = int(category.id)
			cursor.execute("SELECT id FROM status where id=%s and guild=%s", (3, guild))
			if cursor.fetchone()==None:
				cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (3, True, category1, guild))
			else:
				cursor.execute('UPDATE status SET arg=%s where id=%s and guild=%s', (category1, 3, guild))
			connection.commit()
			embed=interactions.Embed(color =0x2ecc71, description=f"Категория для тикетов успешно настроена на **{category.name}**")
			await ctx.send(embeds=embed)
		else:
			embed=interactions.Embed(color =0xf50a19, description=f"Это не категория")
			await ctx.send(embeds=embed)
	elif sub_command=="requests":
		channel1 = int(channel.id)
		if channel.type == interactions.ChannelType.GUILD_TEXT:
			cursor.execute("SELECT id FROM status where id=%s and guild=%s", (2, guild))
			if cursor.fetchone()==None:
				cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (2, True, channel1, guild))
			else:
				cursor.execute('UPDATE status SET arg=%s, status=%s where id=%s and guild=%s', (channel1, True,  2, guild))
			connection.commit()
			await channel.modify(nsfw=True)
			await ctx.send(embeds=interactions.Embed(color=0x14e34b, description=f"Канал для получения запросов успешно настроен на {channel.mention}"))
		else:
			await ctx.send("Канал не текствого типа")
	elif sub_command=="nsfw":
		channel1 = int(channel.id)
		if channel.type == interactions.ChannelType.GUILD_TEXT:
			cursor.execute("SELECT id FROM status where id=%s and guild=%s", (4, guild))
			if cursor.fetchone()==None:
				cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (4, True, channel1, guild))
			else:
				cursor.execute('UPDATE status SET arg=%s, status=%s where id=%s and guild=%s', (channel1, True,  4, guild))
			connection.commit()
			await ctx.send(embeds=interactions.Embed(color=0x14e34b, description=f"Канал для получения NSFW(18+) рассылки успешно настроен на {channel.mention}"))
		else:
			await ctx.send("Канал не текствого типа")

@bot.command(
	name="ticket",
	description="None",
	options=[
		interactions.Option(
			name="claim",
			description="Создать сделку",
			type=interactions.OptionType.SUB_COMMAND,
		),
		interactions.Option(
			name="add",
			description="Добавить участника в сделку",
			type=interactions.OptionType.SUB_COMMAND,
			options= [
				interactions.Option(
					name="user",
					description="Участник которого желаете добавить",
					type=interactions.OptionType.USER,
					required=True,
			),
		],
		),
		interactions.Option(
			name="kick",
			description="Удалить участника из сделки",
			type=interactions.OptionType.SUB_COMMAND,
			options=[ 
				interactions.Option(
					name="user",
					description="Участник которого желаете удалить",
					type=interactions.OptionType.USER,
					required=True,
			),
		]
		),
		interactions.Option(
			name="close",
			description="Закрыть сделку",
			type=interactions.OptionType.SUB_COMMAND,
		),
	],
)
async def ticket(ctx, sub_command: str, user = None):
	member = user
	await ctx.defer()
	if sub_command=="claim":
		guild = int(ctx.guild_id)
		author = int(ctx.author.id)
		cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
		if cursor.fetchone() == None:
			cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
			connection.commit()
		else:
			pass
		cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
		for row in cursor.fetchone():
			channel = row
			try:
				channel1 = await get(bot, interactions.Channel, channel_id=channel)
				call = channel1.id
			except:
				author = int(ctx.author.id)
				guild = int(ctx.guild_id)
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
		cursor.execute("SELECT stat FROM counter where author=%s and guild=%s", (author, guild))
		for row in cursor.fetchone():
			count = row
			if count==True:
				await ctx.send(embeds =interactions.Embed(description=f"**У тебя уже есть сделка <#{channel1.id}>**"))
			else:
				author = int(ctx.author.id)
				guild = int(ctx.guild_id)
				await asyncio.sleep(0.5)
				cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
				for row in cursor.fetchone():
					categ =row
					try:
						guild = int(ctx.guild_id)
						cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
						for row in cursor.fetchone():
							categ =row
							category = await get(bot, interactions.Channel, channel_id=categ)
							category1=int(category.id)
					except:
						category1=None
					finally:
						author = int(ctx.author.id)
						guild1 =  await interactions.get(bot, interactions.Guild, object_id=int(ctx.guild_id))
						channel = await guild1.create_channel(name=f'сделка-{ctx.author.name}', type= interactions.ChannelType.GUILD_TEXT, parent_id=category1)
						user= ctx.author
						channel1 = int(channel.id)
						overwrites = channel.permission_overwrites
						if overwrites is None:
							overwrites = []
						overwrites.append(
        					interactions.Overwrite(
								type=1,
								id=int(ctx.author.id),
								allow=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
       						)
    					)
						overwrites.append(
							interactions.Overwrite(
								type=0,
								id=int(guild1.id),
								deny=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
	   						)
						)
						await channel.modify(permission_overwrites=overwrites)
						cursor.execute('UPDATE counter SET stat=%s,channel = %s where author=%s and guild=%s', (True, channel1, author, guild))
						connection.commit()
						await ctx.send(embeds=interactions.Embed(description=f"**Тикет <#{channel.id}> успешно создан <@{ctx.author.id}>**"))
						await channel.send(embeds=interactions.Embed(description=f"**Тикет успешно создан <@{ctx.author.id}>**"))
	elif sub_command=="add":
		await ctx.get_channel()
		author = int(ctx.author.id)
		guild = int(ctx.guild_id)
		cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
		if cursor.fetchone() == None:
			cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
			connection.commit()
		cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
		for row in cursor.fetchone():
			channel1id = row
			try:
				cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
				for row in cursor.fetchone():
					channel1id = row
					guild1 = await interactions.get(bot, interactions.Guild, object_id=int(ctx.guild_id))
					channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
					call = channel1.id
			except:
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
			else:
				try:
					user= await get(bot, interactions.User, user_id=int(member.id))
				except:
					await ctx.send("Участника нет на сервере")
			cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
			for row in cursor.fetchone():
				if row == 0:
					await ctx.send(embeds=interactions.Embed(description=f"**У тебя нет сделок сейчас**"))
			channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
			user= await get(bot, interactions.User, user_id=int(member.id))
			overwrites = channel1.permission_overwrites
			if overwrites is None:
				overwrites = []
			overwrites.append(
        		interactions.Overwrite(
					type=1,
					id=int(member.id),
					allow=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
       			)
       		)
			await channel1.modify(permission_overwrites=overwrites)
			try:
				guild = await interactions.get(bot, interactions.Guild, object_id=int(ctx.guild_id))
				role = await get(bot, interactions.Role, guild_id = int(ctx.guild_id), role_id=936505743987867659)
				await guild.add_member_role(role.id, member.id)
			except:
				pass
			await channel1.send(f"Здравствуйте <@{member.id}>.")
			await ctx.send("Участник успешно добавлен.",embeds=interactions.Embed(description=f"**Участник <@{member.id}> успешно добавлен в <#{channel1.id}>.**"))
			
	elif sub_command =="kick":
		author = int(ctx.author.id)
		guild = int(ctx.guild_id)
		cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
		if cursor.fetchone() == None:
			cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
			connection.commit()
		cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
		for row in cursor.fetchone():
			channel1id = row
			try:
				cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
				for row in cursor.fetchone():
					channel1id = row
					guild1 = await interactions.get(bot, interactions.Guild, object_id=int(ctx.guild_id))
					channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
					call = channel1.id
			except:
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
			else:
				try:
					user= await get(bot, interactions.User, user_id=int(member.id))
				except:
					await ctx.send("Участника нет на сервере")
			cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
			for row in cursor.fetchone():
				if row == 0:
					await ctx.send(embeds=interactions.Embed(description=f"**У тебя нет сделок сейчас**"))
			channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
			user= await get(bot, interactions.User, user_id=int(member.id))
			overwrites = channel1.permission_overwrites
			if overwrites is None:
				overwrites = []
			overwrites.append(
        		interactions.Overwrite(
					type=1,
					id=int(member.id),
					deny=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
       			)
       		)
			await channel1.modify(permission_overwrites=overwrites)
			try:
				guild = await interactions.get(bot, interactions.Guild, object_id=int(ctx.guild_id))
				role = await get(bot, interactions.Role, guild_id = int(ctx.guild_id), role_id=936505743987867659)
				await guild.add_member_role(role.id, member.id)
			except:
				pass
			await channel1.send(f"Прощайте <@{member.id}>.")
			await ctx.send(embeds=interactions.Embed(description=f"**Участник <@{member.id}> успешно удалён из <#{channel1.id}>.**"))

	elif sub_command=="close":
		author = int(ctx.author.id)
		guild = int(ctx.guild_id)
		cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
		if cursor.fetchone() == None:
			cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
			connection.commit()
		cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
		for row in cursor.fetchone():
			channel1id = row
			try:
				channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
				call = channel1.id
			except:
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
				await ctx.send(embeds=interactions.Embed(description=f"**У тебя нет сделок**"))
			else:
				channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
				overwrites = channel1.permission_overwrites
				if overwrites is None:
					overwrites = []
				overwrites.append(
        			interactions.Overwrite(
						type=1,
						id=int(ctx.author.id),
						deny=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
       				)
       			)
				await channel1.modify(permission_overwrites=overwrites)
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
				await ctx.send("Сделка закрыта")
				await channel1.send(embeds=interactions.Embed(description=f"**Больше создатель сделки не имеет к ней доступа**"))		
@bot.command(
	name="destroy",
	description="Удалить сделку",
	default_member_permissions=interactions.Permissions.ADMINISTRATOR,
	options=[interactions.Option(
		name="channel",
		description="Сделка которую удалить",
		type=interactions.OptionType.CHANNEL,
		required=False,
	),]
)
async def destroy(ctx, channel = None):
	if channel == None:
		channel = await ctx.get_channel()
	await ctx.defer()
	guild = int(ctx.guild_id)
	try:
		guild = int(ctx.guild_id)
		cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
		for row in cursor.fetchone():
			categ =row
			category = await get(bot, interactions.Channel, channel_id=categ)
			category1=int(category.id)
	except:
		cursor.execute("UPDATE status SET status=%s, arg=%s WHERE id=%s and guild=%s", (False, 0, 3, guild))
		connection.commit()
	if channel.type != interactions.ChannelType.GUILD_CATEGORY:
		cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
		if cursor.fetchone()==None:
			await ctx.send(embeds=interactions.Embed(color=0xf50a19, description="**Категория для сделок не настроена**"))
		else:
			cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
			for row in cursor.fetchone():
				cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
				if row == 0:
					await ctx.send(embeds=interactions.Embed(color=0xf50a19, description="**Категория для сделок не настроена**"))
				else:
					cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
					for row in cursor.fetchone():
						category = row
						if channel.parent_id ==None:
							parent =1
						else:
							parent = int(channel.parent_id)
						if  parent == category:
							await channel.delete()
							await ctx.send(embeds=interactions.Embed(description="**Сделка успешно удалена**"))
						else:
							await ctx.send(embeds=interactions.Embed(color=0xf50a19, description="**Канал не в той категории**"))
	else:
		await ctx.send(embeds=interactions.Embed(color=0xf50a19,description="**Зачем-же категорию удалять?**"))
	

@bot.command(
	name="vip",
	description="None",
	options=[
		interactions.Option(
			name="am",
			description="Приватный сервер Адопт Ми",
			type=interactions.OptionType.SUB_COMMAND,
		),
		interactions.Option(
			name="mm2",
			description="Приватный сервер Мардер Мистери",
			type=interactions.OptionType.SUB_COMMAND,
		),
		interactions.Option(
			name="psx",
			description="Приватный сервер PSX",
			type=interactions.OptionType.SUB_COMMAND,
		),
	],
)
async def vip(ctx, sub_command: str):
	await ctx.defer()
	if sub_command == "am":
		await ctx.send(embeds=interactions.Embed(description=f"**Приватный сервер в адопте: [Нажми сюда что-бы зайти](https://www.roblox.com/games/920587237?privateServerLinkCode=41122651371977856802806669923465)**"))
	elif sub_command == "mm2":
		await ctx.send(embeds=interactions.Embed(description=f"**Приватный сервер в мардер мистери: [Нажми сюда что-бы зайти](https://www.roblox.com/games/142823291?privateServerLinkCode=89852226291968909722581151698927)**"))
	elif sub_command =="psx":
		await ctx.send(embeds=interactions.Embed(description=f"**Приватный сервер в пет симулятор X: [Нажми сюда что-бы зайти](https://www.roblox.com/games/6284583030/x3-Pet-Simulator-X?privateServerLinkCode=55975160176260713274764851250283)**"))

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
async def balance(ctx, user = None):
	pass

button = interactions.Button(
	style=interactions.ButtonStyle.PRIMARY,
	label="Нужна сделка",
	custom_id="request"
)

@bot.command(
    name="setup",
    description="Установить запрос на сделки",
	default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def setup(ctx):
	await ctx.defer()
	cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (2, int(ctx.guild_id)))
	if cursor.fetchone() is None:
		await ctx.send("Не настроен канал для получения запросов", ephemeral=True)
	else:
		cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (2, int(ctx.guild_id)))
		for row in cursor.fetchone():
			if row == False:
				await ctx.send("Информация о канале для запросов устарела", ephemeral=True)
			else:
				await ctx.send(embeds=interactions.Embed(description="**Создать запрос на сделку**"), components=button)

async def cooldown_error_form(ctx, amount):
	t = amount.total_seconds()
	a = int(str(time.time()).split('.')[0])
	b = int(str(t).split('.')[0])
	timestamps = a+b
	await ctx.send(f"Ты уже отправил запрос, <t:{timestamps}:R> сможешь опять.", ephemeral=True)

@bot.component("request")
async def button_response(ctx):
	modal = interactions.Modal(
		title="Форма запроса",
		custom_id="request_form",
        components=[
	        interactions.TextInput(
				style=interactions.TextStyleType.SHORT,
				label="ID участника с которым сделка",
				custom_id="text_input_response",
				min_length=18,
				max_length=18,
				required=True,
			),
			interactions.TextInput(
				style=interactions.TextStyleType.SHORT,
				label="Что получит гарант",
				custom_id="text_input_response2",
				max_length=100,
				required=True,
			),
			interactions.TextInput(
				style=interactions.TextStyleType.PARAGRAPH,
				label="Подробности сделки",
				custom_id="text_input_response3",
				max_length=200,
				required=False,
			),
		],
	)
	await ctx.popup(modal)

@bot.modal("request_form")
@cooldown(seconds=600, error=cooldown_error_form, type="user")
async def modal_response(ctx, response = str, response2 = str, response3 = None):
	await ctx.defer(ephemeral=True)
	try:
		m_id=int(response)
		member = await get(bot, interactions.User, user_id=m_id)
		print(member)
	except:
		await ctx.send(f"Неверно указан ID", ephemeral=True)
	else:
		if int(response) == int(ctx.author.id):
			await ctx.send(f"Нельзя указать себя", ephemeral=True)
		else:
			author = int(ctx.author.id)
			guild = await interactions.get(bot, interactions.Guild, object_id=int(ctx.guild_id))
			guild1 = int(guild.id)
			cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, guild1))
			for row in cursor.fetchone():
				channel = row
				try:
					channel1 = await interactions.get(bot, interactions.Channel, object_id=channel)
					call = channel1.id
				except:
					author = int(ctx.author.id)
					guild = int(ctx.guild_id)
					cursor.execute("UPDATE status SET status=%s, arg=%s where id=%s and guild=%s", (False, 0, 2, guild))
					connection.commit()
				finally:
					embed = interactions.Embed(
						title=f"Создал запрос на сделку",
						description=f"**Второй участник сделки {member.mention} [{member.id}]**\n\n**Гарант получит:** {response2}",
						color=0x0ddb14,
						timestamp=datetime.datetime.now()
					)
					embed.set_author(name=f"{ctx.author.name}#{ctx.author.user.discriminator} [{ctx.author.id}]", icon_url=ctx.author.user.avatar_url)
					if response3:
						embed.add_field(
							name="Подробности сделки:",
							value=f"{response3}",
							inline=True
						)
					cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (2, int(ctx.guild_id)))
					for row in cursor.fetchone():
						if row == False:
							await ctx.send(f"Информация о канале для получения форм устарела. Пожалуйста, сообщите администраторам")
						else:
							await channel1.send(embeds=embed)
							await ctx.send(f"Форма успешно отправлена")




bot.start()