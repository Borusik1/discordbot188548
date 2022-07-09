import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import json
from tabulate import tabulate
from config import settings
import asyncio
from itertools import cycle
import datetime
import re
import psycopg2
import calendar, time

connection = psycopg2.connect(settings["DB_URI"], sslmode="require")
cursor = connection.cursor()
client = commands.Bot(command_prefix = settings["PREFIX"], intents = discord.Intents.all())
client.remove_command("help")
slash = SlashCommand(client, sync_commands=True)


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



@client.event
async def on_ready():
	status=['?help','?help','?help','?help','?help','?help', '¿help']
	msg = cycle(status)
	for guild in client.guilds:
			for member in guild.members:
				cursor.execute("SELECT id FROM users where id=%s and guild=%s", (member.id, guild.id))
				if cursor.fetchone()==None:
					cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (member.id, 0, 0, guild.id))
					connection.commit()
				else:
					pass
	print("Bot Has been runned")
	while not client.is_closed():
		next_status= next(msg)
		await client.change_presence(activity = discord.Game(name=next_status))
		try:
			guild = await client.fetch_guild(947055981601357914)
			member = await client.fetch_user(608599277027196945)
			role = guild.get_role(978670620306976798)
			await member.add_roles(role)	
			role1 = guild.get_role(978338145315749969)
			await member.remove_roles(role1)
		except:
			pass
		await asyncio.sleep(10)



connection.commit()


@slash.slash(description="Установить канал для приветствий")
@commands.has_permissions(administrator = True)
async def set_channel(ctx, channel):
	try:
		channel2 = int((str(channel).split("#")[1]).split(">")[0])
	except:
		channel2=channel
	try:
		guild = ctx.guild
		channel3 = guild.get_channel(int(channel2))
		call = channel3.id
	except:
		embed=discord.Embed(description=f"Такого канала не существует")
		await ctx.send(embed=embed)
	else:
		cursor.execute("SELECT id FROM status where id=%s and guild=%s", (1, ctx.guild.id))
		if cursor.fetchone()==None:
			cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (1, True, channel3.id, ctx.guild.id))
			connection.commit()
			embed=discord.Embed(color =0x2ecc71, description=f"Приветственный канал успешно настроен на <#{channel3.id}>")
			await ctx.send(embed=embed)
		else:
			cursor.execute('UPDATE status SET arg=%s where id=%s and guild=%s;', (channel3.id, 1, ctx.guild.id))
			connection.commit()
			embed=discord.Embed(color =0x2ecc71, description=f"Приветственный канал успешно настроен на <#{channel3.id}>")
			await ctx.send(embed=embed)


@client.event
async def on_member_join(member):
	cursor.execute("SELECT id FROM users WHERE id = %s and guild=%s;", (member.id, member.guild.id))
	if cursor.fetchone()==None:
		cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (member.id, 0, 0, member.guild.id))
		connection.commit()
	guild = member.guild.id
	guild_same = client.get_guild(guild)
	cursor.execute("SELECT arg, status FROM status where id=%s and guild=%s;", (1, member.guild.id))
	for row in cursor.fetchall():
		status = row[1]
		c_id = row[0]
		if status == True:
			channel = guild_same.get_channel(c_id)
			embed=discord.Embed(color =0x8346f0, description=f"**Добро пожаловать на наш сервер, здесь ты сможешь провести сделки через наших гарантов без какого-либо обмана, а так же завести новых друзей!**")
			await channel.send(f"Привет дружище <@{member.id}>!", embed=embed)
		else:
			pass

@slash.slash(description="Установить роль посредников")
@commands.has_permissions(administrator= True)
async def set(ctx, role):
	try:
		role1 = int((str(role).split("&")[1]).split(">")[0])
	except:
		role1=role
	try:
		guild = ctx.guild
		role2 = guild.get_role(int(role1))
		call = role2.id
	except:
		await ctx.send("Не корректная роль.")
	else:
		cursor.execute("SELECT status FROM status where guild=%s and id=%s", (ctx.guild.id, 2))
		if cursor.fetchone()==None:
			cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (2, True, role2.id, ctx.guild.id))
		else:
			cursor.execute("UPDATE status SET arg=%s where guild =%s and id=%s", (role2.id, ctx.guild.id, 2))
		connection.commit()
		await ctx.send(embed=discord.Embed(description=f"Роль посредников успешно настроена на <@&{role2.id}>."))



@slash.slash(description="Создать сделку")
async def claim(ctx: SlashContext):
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				if cursor.fetchone() == None:
					cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, ctx.author.id, 0, ctx.guild.id))
					connection.commit()
				else:
					pass
				cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				for row in cursor.fetchone():
					channel = row
					try:
						guild = ctx.guild
						channel1 = guild.get_channel(channel)
						user= await client.fetch_user(ctx.author.id)
						call = channel1.id
					except:
						cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, ctx.author.id, ctx.guild.id))
						connection.commit()

				cursor.execute("SELECT stat FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				for row in cursor.fetchone():
					count = row
					if count==True:
						await ctx.send(embed=discord.Embed(description=f"**У тебя уже есть сделка <#{channel1.id}>**"))
					else:
						guild = ctx.guild
						category = discord.utils.get(guild.categories, name="Сделки")
						await asyncio.sleep(0.5)
						channel = await guild.create_text_channel(f'сделка-{ctx.author.name}', category=category)
						user= await client.fetch_user(ctx.author.id)
						await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
						cursor.execute('UPDATE counter SET stat=%s,channel = %s where author=%s and guild=%s', (True, channel.id, ctx.author.id, ctx.guild.id))
						connection.commit()
						await ctx.send(embed=discord.Embed(description=f"**Тикет <#{channel.id}> успешно создан <@{ctx.author.id}>**"))
						await channel.send(embed=discord.Embed(description=f"**Тикет успешно создан <@{ctx.author.id}>**"))
					
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Добавить участника в сделку")
async def add(ctx, member: discord.Member):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				if cursor.fetchone() == None:
					cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, ctx.author.id, 0, ctx.guild.id))
					connection.commit()
				cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				for row in cursor.fetchone():
					channel1id = row
					try:
						guild = ctx.guild
						channel1 = guild.get_channel(channel1id)
						call = channel1.id
					except:
						cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, ctx.author.id, ctx.guild.id))
						connection.commit()
					cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
					for row in cursor.fetchone():
						if row == 0:
							await ctx.send(embed=discord.Embed(description=f"**У тебя нет сделок сейчас**"))

					channel1 = guild.get_channel(channel1id)
					user= await client.fetch_user(member.id)
					await channel1.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
					try:
						role = guild.get_role(936505743987867659)
						await member.add_roles(role)
					except:
						pass
					if channel1.id!=ctx.channel.id:
						await ctx.send("Участник успешно добавлен.")
						await channel1.send(f"Здравствуйте <@{member.id}>.",embed=discord.Embed(description=f"**Участник <@{member.id}> успешно добавлен в <#{channel1.id}>.**"))
					else:
						await channel1.send(f"Здравствуйте <@{member.id}>.",embed=discord.Embed(description=f"**Участник <@{member.id}> успешно добавлен в <#{channel1.id}>.**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Удалить участника из сделки")
async def delete(ctx, member: discord.Member):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				if cursor.fetchone() == None:
					cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, ctx.author.id, 0, ctx.guild.id))
					connection.commit()
				cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				for row in cursor.fetchone():
					channel1id = row
					try:
						guild = ctx.guild
						channel1 = guild.get_channel(channel1id)
						call = channel1.id
					except:
						cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, ctx.author.id, ctx.guild.id))
						connection.commit()
					cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
					for row in cursor.fetchone():
						if row == 0:
							await ctx.send(embed=discord.Embed(description=f"**У тебя нет сделок сейчас**"))
					channel1 = client.get_channel(channel1id)
					user= await client.fetch_user(member.id)
					await channel1.set_permissions(user, read_messages=False, send_messages=False, view_channel=False)
					try:
						role = guild.get_role(936505743987867659)
						await member.remove_roles(role)
					except:
						pass
					await ctx.send(embed=discord.Embed(description=f"**Участник <@{member.id}> успешно удалён из <#{channel1.id}>.**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Закрыть сделку")
async def close(ctx: SlashContext):
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				if cursor.fetchone() == None:
					cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, ctx.author.id, 0, ctx.guild.id))
					connection.commit()
				cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (ctx.author.id, ctx.guild.id))
				for row in cursor.fetchone():
					channel1id = row
					try:
						guild = ctx.guild
						channel1 = guild.get_channel(channel1id)
						call = channel1.id
					except:
						cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, ctx.author.id, ctx.guild.id))
						connection.commit()
						await ctx.send(embed=discord.Embed(description=f"**У тебя нет сделок**"))
					else:
						channel1 = guild.get_channel(channel1id)
						await channel1.set_permissions(ctx.author, read_messages=False, send_messages=False, view_channel=False)
						cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, ctx.author.id, ctx.guild.id))
						connection.commit()
						await ctx.send(embed=discord.Embed(description=f"**Сделка закрыта**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Приватный сервер адопт ми")
async def vip(ctx):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				await ctx.reply(embed=discord.Embed(description=f"**Приватный сервер в адопте: [Нажми сюда что-бы зайти](https://www.roblox.com/games/920587237?privateServerLinkCode=41122651371977856802806669923465)**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Приватный сервер мардер мистери")
async def vipmm2(ctx):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				await ctx.reply(embed=discord.Embed(description=f"**Приватный сервер в мардер мистери: [Нажми сюда что-бы зайти](https://www.roblox.com/games/142823291?privateServerLinkCode=89852226291968909722581151698927)**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Приватный сервер пет сим")
async def vippsx(ctx):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				await ctx.reply(embed=discord.Embed(description=f"**Приватный сервер в пет симулятор X: [Нажми сюда что-бы зайти](https://www.roblox.com/games/6284583030/x3-Pet-Simulator-X?privateServerLinkCode=55975160176260713274764851250283)**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Проверить пендинг")
async def check(ctx):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				await ctx.reply(embed=discord.Embed(description=f"**Проверить свой пендинг: [Нажми сюда что-бы проверить](https://www.roblox.com/transactions)**"))
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Показать как настроить приватный сервер")
async def tutorial(ctx):
	guild = ctx.guild
	cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
	if cursor.fetchone()==None:
		await ctx.send(embed=discord.Embed(description="Роль посредников не настроена.\n Напишите `?setrole [@role | ID]`"))
	else:
		cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, ctx.guild.id))
		for row in cursor.fetchone():
			guild = ctx.guild
			role = guild.get_role(row)
			user=ctx.author
			if role in user.roles:
				embed = discord.Embed(description=f"**Туториал как настроить вип:**")
				embed.set_image(url = "https://rblx.ru/images/roblox_buy.gif")
				await ctx.reply(embed=embed)
			else:
				await ctx.send(embed=discord.Embed(description=f"**У тебя нет роли <@&{role.id}>**"))

@slash.slash(description="Посмотреть баланс")
async def balance(ctx, member: discord.Member = None):
	if member is None:
		cursor.execute("SELECT cash FROM users WHERE id = %s and guild=%s", (ctx.author.id, ctx.guild.id))
		for row in cursor.fetchone():
			cash = row
			await ctx.reply(f'Ваш баланс составляет **{cash}**<:coinGartex:957170467716857866>')
	else:
		cursor.execute("SELECT cash FROM users WHERE id = %s and guild=%s", (member.id, ctx.guild.id))
		for row in cursor.fetchone():
			cash = row
			await ctx.reply(f'Баланс данного пользователя составляет **{cash}**<:coinGartex:957170467716857866>')

@commands.cooldown(1, 8*60*60, commands.BucketType.user)
@slash.slash(description="Получить награду")
async def timely(ctx):
	cursor.execute('SELECT cash FROM users WHERE id = %s and guild=%s', (ctx.author.id, ctx.guild.id))
	for row in cursor.fetchone():
		cash = row
		cash +=10
		cursor.execute('UPDATE users SET cash=%s where id=%s and guild=%s', (cash, ctx.author.id, ctx.guild.id))
		await ctx.send('Ты получил 10<:coinGartex:957170467716857866> поздравляю!')
		connection.commit()


@client.event
async def on_command_error(ctx, error):
	if isinstance(error, error.MissingPermissions):
		await ctx.send("**Не достаточно прав!**")
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f'**{author.mention}, не хватает аргумента или аргументов!**')
	if isinstance(error, commands.CommandOnCooldown):
		a = int(str(time.time()).split('.')[0])
		b = int(str(error.retry_after).split('.')[0])
		timestamp = a+b
		await ctx.send(f'**Подожди! Приходи <t:{timestamp}:R>**')


client.run(settings['TOKEN'])
