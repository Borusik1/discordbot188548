from unicodedata import category
from aiohttp import request
import interactions
from interactions.ext.get import get
import json
from tabulate import tabulate
from config import settings
import asyncio
from itertools import cycle
import datetime
import re
import psycopg2
import calendar, time
import discord
from logging import basicConfig, DEBUG

#basicConfig(level=DEBUG)
bot = interactions.Client("OTE3MDMwMjM4NTk1MjA3MTY4.Yayw9g.1rYs1KWblY90oTXxwGXPlsTXdOQ", intents = interactions.Intents.ALL)
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

@bot.event
async def on_ready():
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
	i = 1 
	while i==1:
		await bot.change_presence(interactions.ClientPresence(activities=[interactions.PresenceActivity(name="только slash-commands", type=interactions.PresenceActivityType.GAME)]))
		guild = await get(bot, interactions.Guild, guild_id=947055981601357914)
		member = await get(bot, interactions.Member, guild_id = int(guild.id), member_id=608599277027196945)
#		role = await get(bot, interactions.Role, guild_id = int(guild.id), role_id=)
#		await guild.add_member_role(role.id, member.id)	
		role1 = await get(bot, interactions.Role, guild_id = int(guild.id), role_id=978338145315749969)
		await guild.remove_member_role(role1.id, member.id)
		await asyncio.sleep(10)

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
			options= [interactions.Option(
				name="member",
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
			options=[ interactions.Option(
				name="member",
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
async def ticket(ctx, sub_command: str, member = None):
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
			finally:
				pass
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
						guild1 =  await ctx.get_guild()
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
					guild1 = await ctx.get_guild()
					channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
					call = channel1.id
			except:
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
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
				guild = await ctx.get_guild()
				role = await get(bot, interactions.Role, guild_id = int(ctx.guild_id), role_id=936505743987867659)
				await guild.add_member_role(role.id, member.id)
			except:
				pass
			await channel1.send(f"Здравствуйте <@{member.id}>.")
			await ctx.send("Участник успешно добавлен.",embeds=interactions.Embed(description=f"**Участник <@{member.id}> успешно добавлен в <#{channel1.id}>.**"))
			
	elif sub_command =="kick":
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
					guild1 = await ctx.get_guild()
					channel1 = await get(bot, interactions.Channel, channel_id=channel1id)
					call = channel1.id
			except:
				cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
				connection.commit()
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
				guild = await ctx.get_guild()
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
				await channel1.send(embeds=interactions.Embed(description=f"**Больше создатель сделки не имеет к ней доступа"))		
@bot.command(
	name="destroy",
	description="Удалить сделку",
	default_member_permissions=interactions.Permissions.ADMINISTRATOR,
	options=[interactions.Option(
		name="channel",
		description="Сделка которую удалить",
		type=interactions.OptionType.CHANNEL,
		requered=False,
	),]
)
async def destroy(ctx, channel = None):
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
	if channel != None:
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
								await ctx.send(embeds=interactions.Embed(description="Сделка успешно удалена"))
							else:
								await ctx.send(embeds=interactions.Embed(color=0xf50a19, description="**Канал не в той категории**"))
		else:
			await ctx.send(embeds=interactions.Embed(color=0xf50a19,description="**Зачем-же категорию удалять?**"))
	else:
		channel1 = await ctx.get_channel()
		if channel1.type != interactions.ChannelType.GUILD_CATEGORY:
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
							if channel1.parent_id ==None:
								parent =1
							else:
								parent = int(channel1.parent_id)
							if  parent == category:
								await channel1.delete()
								await ctx.send(embeds=interactions.Embed(description="Сделка успешно удалена"))
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

bot.start()