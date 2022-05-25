import discord
from discord.ext import commands
import json
import sqlite3
from tabulate import tabulate
from config import settings
from asyncio import sleep

client = commands.Bot(command_prefix = settings['PREFIX'], intents = discord.Intents.all())
client.remove_command("help")
connection = sqlite3.connect('server.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
	id INT,
	cash INT,
	rep INT
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS status (
	id INTEGER PRIMARY KEY,
	status BOOL,
	arg TEXT
	)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS counter (
	stat BOOL,
	author INT,
	channel INT
	)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS tickets (
	stat BOOL,
	author INT,
	channel INT
	)""")


connection.commit()
for row in cursor.execute("SELECT * FROM counter"):
	print(row)

@client.event
async def on_ready():
	print("Bot Has been runned")
	game = discord.Game("?help")
	await client.change_presence(activity=game)
	for guild in client.guilds:
		for member in guild.members:
			cursor.execute(f"SELECT id FROM users where id={member.id}")
			if cursor.fetchone()==None:
				cursor.execute(f"INSERT INTO users VALUES ({member.id}, 0 , 0)")
				connection.commit()
			else:
				pass


connection.commit()


@client.command()
@commands.has_role(933672340150165714)
async def set_wave_channel(ctx, channel):
	cursor.execute("SELECT id FROM status where id=1")
	if cursor.fetchone()==None:
		cursor.execute(f"INSERT INTO status VALUES (?, ?, ?)",(1, False, 0))
		connection.commit()
	else:
		pass
	cursor.execute("UPDATE status SET status = True where id=1")
	cursor.execute(f'UPDATE status SET arg={channel} where id=1')
	connection.commit()
	embed=discord.Embed(color =0x2ecc71, description=f"Приветственный канал успешно настроен на {channel}")
	await ctx.send(embed=embed)


@client.event
async def on_member_join(member):
	for row in cursor.execute("SELECT arg, status FROM status where id=1"):
		status = row[1]
		c_id = row[0]
		if status == True:
			channel = client.get_channel(c_id)
			if member.id == 894893094594564156:
				embed=discord.Embed(color =0x8346f0, description=f"**Привет заюша это приветствие специально для тебя от <@608599277027196945>**")
				await channel.send(f"Привет <@{member.id}>!", embed=embed)
			else:
				embed=discord.Embed(color =0x8346f0, description=f"**Добро пожаловать на наш сервер, здесь ты сможешь провести сделки через наших гарантов без какого-либо обмана, а так же завести новые общения!**")
				await channel.send(f"Привет дружище <@{member.id}>!", embed=embed)
				cursor.execute(f"SELECT id FROM users WHERE id = {member.id}")
			if cursor.fetchone()==None:
				cursor.execute(f"INSERT INTO users VALUES ({member.id} , 0 , 0)")
				connection.commit()
		else:
			pass

@client.command()
@commands.has_role(933672340150165714 or 926469565343477760)
async def setup(ctx):
	msg = await ctx.send(
		embed = discord.Embed(title = 'Нужна сделка?'),
		components = [
			Button(style = ButtonStyle.green, label = 'Да', custom_id="Yes")
        ])


@client.command(aliases=["create"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def claim(ctx):
	uid = ctx.author.id
	cursor.execute(f"SELECT author FROM counter where author={uid}")
	if cursor.fetchone() == None:
		cursor.execute(f"INSERT INTO counter VALUES (False, {uid}, 0)")
		connection.commit()
	else:
		pass
	for row in cursor.execute(f"SELECT channel FROM counter where author={uid}"):
		channel = row[0]
		try:
			guild = ctx.message.guild
			channel1 = guild.get_channel(channel)
			user= await client.fetch_user(uid)
			await channel1.set_permissions(user, read_messages=True, send_messages=True, view_channel=True, manage_channels=True)
		except:
			cursor.execute(f"UPDATE counter SET stat=False, channel=0 where author={uid}")
			connection.commit()


	for row in cursor.execute(f"SELECT stat FROM counter where author={uid}"):
		count = row[0]
		if count == False:
			guild = ctx.message.guild
			category = discord.utils.get(guild.categories, name="Сделки")
			channel = await guild.create_text_channel(f'сделка-{ctx.author.name}', category=category)
			user= await client.fetch_user(uid)
			await channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True, manage_channels=True)
			cursor.execute(f'UPDATE counter SET stat=True,channel = {channel.id} where author={uid}')
			connection.commit()
			await ctx.send(embed=discord.Embed(description=f"**Тикет <#{channel.id}> успешно создан <@{ctx.author.id}>**"))
			await channel.send(embed=discord.Embed(description=f"**Тикет успешно создан <@{ctx.author.id}>**"))

@client.command(aliases=["+"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def add(ctx, member: discord.Member):
	uid = ctx.author.id
	guild = ctx.message.guild
	cursor.execute(f"SELECT author FROM counter where author={uid}")
	if cursor.fetchone() == None:
		cursor.execute(f"INSERT INTO counter VALUES (False, {uid}, 0)")
		connection.commit()
	for row in cursor.execute(f"SELECT channel FROM counter where author={uid}"):
		channel1id = row[0]

		try:
			guild = ctx.message.guild
			channel1 = guild.get_channel(channel1id)
			user= await client.fetch_user(uid)
			await channel1.set_permissions(user, read_messages=True, send_messages=True, view_channel=True, manage_channels=True)
		except:
			cursor.execute(f"UPDATE counter SET stat=False, channel=0 where author={uid}")
			connection.commit()

		channel1 = guild.get_channel(channel1id)
		user= await client.fetch_user(member.id)
		await channel1.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
		try:
			role = guild.get_role(936505743987867659)
			await member.add_roles(role)
		except:
			pass
		await channel1.send(f"Здравствуйте <@{member.id}>.",embed=discord.Embed(description=f"**Участник <@{member.id}> успешно добавлен в <#{channel1.id}>.**"))

@client.command(aliases=["del", "-"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def delete(ctx, member: discord.Member):
	guild = ctx.message.guild
	uid = ctx.author.id
	channel = client.get_channel(ctx.channel.id)
	cursor.execute(f"SELECT author FROM counter where author={uid}")
	if cursor.fetchone() == None:
		cursor.execute(f"INSERT INTO counter VALUES (False, {uid}, 0)")
		connection.commit()
	for row in cursor.execute(f"SELECT channel FROM counter where author={uid}"):
		channel1id = row[0]
		try:
			guild = ctx.message.guild
			channel1 = guild.get_channel(channel1id)
			user= await client.fetch_user(uid)
			await channel1.set_permissions(user, read_messages=True, send_messages=True, view_channel=True, manage_channels=True)
		except:
			cursor.execute(f"UPDATE counter SET stat=False, channel=0 where author={uid}")
			connection.commit()
		channel1 = client.get_channel(channel1id)
		user= await client.fetch_user(member.id)
		await channel1.set_permissions(user, read_messages=False, send_messages=False, view_channel=False)
		try:
			role = guild.get_role(936505743987867659)
			await member.remove_roles(role)
		except:
			pass
		await channel1.send(embed=discord.Embed(description=f"**Участник <@{member.id}> успешно удалён из <#{channel1.id}>.**"))

@client.command()
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def close(ctx):
	uid = ctx.author.id
	guild = ctx.message.guild
	channel = guild.get_channel(ctx.channel.id)
	cursor.execute(f"SELECT author FROM counter where author={uid}")
	if cursor.fetchone() == None:
		cursor.execute(f"INSERT INTO counter VALUES (False, {uid}, 0)")
		connection.commit()
	for row in cursor.execute(f"SELECT channel FROM counter where author={uid}"):
		channel1id = row[0]
		try:
			guild = ctx.message.guild
			channel1 = guild.get_channel(channel1id)
			user= await client.fetch_user(uid)
			await channel1.set_permissions(user, read_messages=True, send_messages=True, view_channel=True, manage_channels=True)
		except:
			cursor.execute(f"UPDATE counter SET stat=False, channel=0 where author={uid}")
			connection.commit()
		channel1 = guild.get_channel(channel1id)
		await channel1.delete()
		

@client.command(aliases=["вип"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def vip(ctx):
	await ctx.reply(embed=discord.Embed(description=f"**Приватный сервер в адопте: [Нажми сюда что-бы зайти](https://www.roblox.com/games/920587237?privateServerLinkCode=41122651371977856802806669923465)**"))

@client.command(aliases=["vipmm", "випмм2", "випмм"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def vipmm2(ctx):
	await ctx.reply(embed=discord.Embed(description=f"**Приватный сервер в мардер мистери: [Нажми сюда что-бы зайти](https://www.roblox.com/games/142823291?privateServerLinkCode=89852226291968909722581151698927)**"))

@client.command(aliases=["виппсх", "виппетсим","vipps","виппет"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def vippsx(ctx):
	await ctx.reply(embed=discord.Embed(description=f"**Приватный сервер в пет симулятор X: [Нажми сюда что-бы зайти](https://www.roblox.com/games/6284583030/x3-Pet-Simulator-X?privateServerLinkCode=55975160176260713274764851250283)**"))

@client.command()
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def check(ctx):
	await ctx.reply(embed=discord.Embed(description=f"**Проверить свой пендинг: [Нажми сюда что-бы проверить](https://www.roblox.com/transactions)**"))

@client.command(aliases=["туториал"])
@commands.has_any_role('👨‍👧‍👦 | Посредник')
async def tutorial(ctx):
	embed = discord.Embed(description=f"**Туториал как настроить вип:**")
	embed.set_image(url = "https://rblx.ru/images/roblox_buy.gif")
	await ctx.reply(embed=embed)

@client.command(aliases = ['$', 'cash', 'баланс', 'деньги', 'бал'])
async def balance(ctx, member: discord.Member = None):
	if member is None:
		uid=ctx.author.id
		cursor.execute(f'SELECT id FROM users where id={uid}')
		if cursor.fetchone() is None:
			cursor.execute(f'INSERT INTO users VALUES ({uid}, 0 , 0)')
			connection.commit()
		for row in cursor.execute(f"SELECT cash FROM users WHERE id = {uid}"):
			cash = row[0]
			await ctx.reply(f'Ваш баланс составляет **{cash}**<:coinGartex:957170467716857866>')
	else:
		uid=member.id
		cursor.execute(f'SELECT id FROM users where id={uid}')
		if cursor.fetchone() is None:
			cursor.execute(f'INSERT INTO users VALUES ({uid}, 0 , 0)')
			connection.commit()
		for row in cursor.execute(f"SELECT cash FROM users WHERE id = {uid}"):
			cash = row[0]
			await ctx.reply(f'Баланс данного пользователя составляет **{cash}**<:coinGartex:957170467716857866>')
@client.command(aliases = ['daily'])
async def timely(ctx):
	uid=ctx.author.id
	cursor.execute(f'SELECT id FROM users where id={uid}')
	if cursor.fetchone() is None:
		cursor.execute(f'INSERT INTO users VALUES ({uid}, 0 , 0)')
		connection.commit()
	for row in cursor.execute(f'SELECT cash FROM users WHERE id = {uid}'):
		cash = row[0]
		cash +=10
		cursor.execute(f'UPDATE users SET cash={cash} where id={uid}')
		await ctx.send('Ты получил 10<:coinGartex:957170467716857866> поздравляю!')
		connection.commit()
@client.command()
async def help(ctx):
	await ctx.send(f"**Для работы всех этих команд нужно иметь роль с названием '👨‍👧‍👦 | Посредник' с эмодзи:**\n?claim - создать сделку\n?add [@Участник | ID] - добавить участника в сделку\n?del [@Участник | ID] - удалить участника со сделки\n?close - закрыть сделку\n?vip - випка в адопте\n?vipmm2 - випка в мм2\n?vippsx - випка в псх\n?check - проверить пендинг\n?tutorial - показать как настроить випку")

client.run(settings['TOKEN'])
