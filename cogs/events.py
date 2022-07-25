import interactions
import psycopg2
from itertools import cycle
import asyncpraw
import asyncio
import random
import json
import time



imgs = []
subreddits = ['hentai', 'porn', "nsfw", "hentaibondage", "yuri", "YuriHentai", "HentaiAnal"]
subs= []

class events(interactions.Extension):
	def __init__(self, bot, connection, cursor, reddit, **kwargs):
		self.bot = bot
		self.connection = connection
		self.cursor = cursor
		self.reddit = reddit

	@interactions.extension_listener
	async def on_start(self):
		await self.bot.change_presence(interactions.ClientPresence(activities=[interactions.PresenceActivity(name="только slash-commands", type=interactions.PresenceActivityType.WATCHING)]))
		await asyncio.sleep(2)
		for guild in self.bot.guilds:
			await asyncio.sleep(2)
			members = await guild.get_all_members()
			for member in members:
				await asyncio.sleep(0.01)
				member1 = int(member.id)
				guild1 = int(guild.id)
				self.cursor.execute("SELECT id FROM users where id=%s and guild=%s", (member1, guild1))
				if self.cursor.fetchone()==None:
					self.cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s)", (member1, 0, 0, guild1, '[]'))
					self.connection.commit()
				else:
					pass
		print("Bot Has been runned")
		print(f"Ping: {self.bot.latency}")
		subred = cycle(subreddits)
		while True:
			next_subred = next(subred)
			await asyncio.sleep(20)
			nsfw1 = await self.reddit.subreddit(next_subred)
			if not subs:
				async for nsfw in nsfw1.hot(limit=300):
					subs.append(nsfw)
			rand_nsfw = random.choice(subs)
			if rand_nsfw.is_self:
				pass
			else:
				if rand_nsfw.title not in imgs:
					url = "https://www.reddit.com"+rand_nsfw.permalink
					embed = interactions.Embed(title=rand_nsfw.title, description=f"Link: {url}")
					embed.set_image(url=rand_nsfw.url)
					embed.set_author(name=f"/{rand_nsfw.subreddit} (hot)")
					for guild in self.bot.guilds:
						guild1 = int(guild.id)
						self.cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (4, guild1))
						if self.cursor.fetchone()!=None:
							self.cursor.execute("SELECT arg, status FROM status WHERE id=%s and guild=%s", (4, guild1))
							for row in self.cursor.fetchall():
								if row[1] == True:
									channel = await interactions.get(self.bot, interactions.Channel, object_id=row[0])
									await channel.set_nsfw(nsfw=True)
									try:
										await channel.send(embeds=embed)
									except:
										pass
									imgs.append(rand_nsfw.title)
			nsfw = await self.reddit.subreddit(next_subred)
			nsfw = nsfw.new(limit=1)
			item = await nsfw.__anext__()
			if item.title not in imgs:
				if item.is_self:
					pass
				else:
					url = "https://www.reddit.com"+item.permalink
					embed = interactions.Embed(title=item.title, description=f"Link: {url}")
					embed.set_image(url=item.url)
					embed.set_author(name=f"/{item.subreddit} (newest)")
					for guild in self.bot.guilds:
						guild1 = int(guild.id)
						self.cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (4, guild1))
						if self.cursor.fetchone()!=None:
							self.cursor.execute("SELECT arg, status FROM status WHERE id=%s and guild=%s", (4, guild1))
							for row in self.cursor.fetchall():
								if row[1] == True:
									channel = await interactions.get(self.bot, interactions.Channel, object_id=row[0])
									await channel.set_nsfw(nsfw=True)
									try:
										await channel.send(embeds=embed)
									except:
										pass
									imgs.append(item.title)

	@interactions.extension_listener
	async def on_guild_member_add(self, member):
		member1 = int(member.id)
		guild = int(member.guild_id)
		self.cursor.execute("SELECT id FROM users WHERE id = %s and guild=%s;", (member1, guild))
		if self.cursor.fetchone()==None:
			self.cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s)", (member1, 0, 0, guild, '[]'))
			self.connection.commit()
		guild1 = member.guild_id
		guild_same = await interactions.get(self.bot, interactions.Guild, object_id=guild1)
		self.cursor.execute("SELECT arg, status FROM status where id=%s and guild=%s;", (1, guild))
		for row in self.cursor.fetchall():
			status = row[1]
			c_id = row[0]
			if status == True:
				channel = await interactions.get(self.bot, interactions.Channel, object_id=c_id)
				embed=interactions.Embed(color =0x8346f0, description=f"**Добро пожаловать на наш сервер, здесь ты сможешь провести сделки через наших гарантов без какого-либо обмана, а так же завести новых друзей!**")
				await channel.send(f"Привет дружище <@{member.id}>!", embeds=embed)
			else:
				pass

	@interactions.extension_listener
	async def on_message_create(self, message):
		try:
			self.cursor.execute("SELECT values FROM message_response WHERE id=%s and author=%s and guild=%s", (1, int(message.author.id), int(message.guild_id)))
			if self.cursor.fetchone()!=None:
				self.cursor.execute("SELECT step, status, values, channel, time, message FROM message_response WHERE id=%s and author=%s and guild=%s", (1, int(message.author.id), int(message.guild_id)))
				for row in self.cursor.fetchall():
					if row[3]==int(message.channel_id):
						if row[1]==True:
							now = int(time.time())
							channel = await interactions.get(self.bot, interactions.Channel, object_id=row[3])
							if now < row[4]:
								step = row[0]
								values = json.loads(row[2])
								message_ed = await channel.get_message(row[5])
								field = message_ed.embeds[0].fields[-1]
								embed =  message_ed.embeds[0]
								context = message.content
								if step==0:
									values.append(message.content)
									encoded = json.dumps(values)
									step +=1
									self.cursor.execute("UPDATE message_response SET step=%s, values=%s WHERE id=%s and author=%s and guild=%s", (step, encoded, 1, int(message.author.id), int(message.guild_id)))
									field.value = context
									embed.add_field(
										name="ID предмета:",
										value="**Введите ID предмета, рекомендую использовать легко запоминающийся 1-2х значные цифры**",
										inline=False
									)
								elif step==1:
									try:
										i_id = int(message.content)
									except:
										await channel.send("Id не в цифровом формате")
									else:
										if i_id >= 0:
											values.append(i_id)
											encoded = json.dumps(values)
											step +=1
											self.cursor.execute("UPDATE message_response SET step=%s, values=%s WHERE id=%s and author=%s and guild=%s", (step, encoded, 1, int(message.author.id), int(message.guild_id)))
											field.value = context
											embed.add_field(
												name="Будет ли предмет продаваться в магазине?",
												value="**Да \ Нет**",
												inline=False
											)
										else:
											await channel.send("Id не может быть отрицательным значением")
								elif step==2:
									if context.upper() == "ДА":
										values.append(True)
										encoded = json.dumps(values)
										step +=1
										self.cursor.execute("UPDATE message_response SET step=%s, values=%s WHERE id=%s and author=%s and guild=%s", (step, encoded, 1, int(message.author.id), int(message.guild_id)))
										field.value = context
										embed.add_field(
											name="Цена предмета:",
											value="Введи цену",
											inline=False
										)			
									elif context.upper() == "НЕТ":
										values.append(False)
										values.append(None)
										encoded = json.dumps(values)
										step +=2
										self.cursor.execute("UPDATE message_response SET step=%s, values=%s WHERE id=%s and author=%s and guild=%s", (step, encoded, 1, int(message.author.id), int(message.guild_id)))
										field.value = context
										embed.add_field(
											name="Можно ли использовать предмет?",
											value="Да / Нет",
											inline=False
										)
									else:
										await channel.send("Только Да / Нет")
								elif step==3:
									try:
										i_cost = int(context)
									except:
										await channel.send("Цена не в цифровом формате")
									else:
										if i_cost > 0:
											values.append(i_cost)
											encoded = json.dumps(values)
											step +=1
											self.cursor.execute("UPDATE message_response SET step=%s, values=%s WHERE id=%s and author=%s and guild=%s", (step, encoded, 1, int(message.author.id), int(message.guild_id)))
											field.value = context
											embed.add_field(
												name="Можно ли использовать предмет?",
												value="Да / Нет",
												inline=False
											)
										else:
											await channel.send("Цена должна быть больше 0")
								elif step==4:
									if context.upper() == "ДА":
										values.append(True)
										encoded = json.dumps(values)
										step +=1
										self.cursor.execute("UPDATE message_response SET step=%s, values=%s WHERE id=%s and author=%s and guild=%s", (step, encoded, 1, int(message.author.id), int(message.guild_id)))
										field.value = context
										embed.add_field(
											name="Введите роль которая будет выдаваться при использовании:",
											value="Упомяни @Роль или введи ID",
											inline=False
										)			
									elif context.upper() == "НЕТ":
										values.append(False)
										values.append(None)
										self.cursor.execute("UPDATE message_response SET time=%s, step=%s, status=%s, values=%s, channel=%s, message=%s WHERE id=%s and author=%s and guild=%s", (None, 0, False, '[]', None, None, 1, int(message.author.id), int(message.guild_id)))
										field.value = context
										self.cursor.execute("INSERT INTO items VALUES (%s, %s, %s, %s, %s, %s, %s)", (values[0], values[1], values[2], values[3], values[4], values[5], int(message.guild_id)))
										await channel.send("Конфигурация окончена")
									else:
										await channel.send("Только Да / Нет")
								elif step==5:
									if message.mention_roles:
										role = message.mention_roles[0]
										role1 = int(role)
									elif message.content.isdigit():
										role = message.content
										try:
											role_ob= await interactions.get(self.bot, interactions.Role, object_id=role)
											role1 = int(role_ob.id)
										except:
											role1 =None
											await channel.send("Это не роль")
									else:
										role1 = None
										await channel.send("Это не роль")
									if role1:
										values.append(role1)
										self.cursor.execute("UPDATE message_response SET time=%s, step=%s, status=%s, values=%s, channel=%s, message=%s WHERE id=%s and author=%s and guild=%s", (None, 0, False, '[]', None, None, 1, int(message.author.id), int(message.guild_id)))
										field.value = f"<@&{role1}>"
										self.cursor.execute("SELECT name FROM items WHERE id=%s and guild=%s", (values[1], int(message.guild_id)))
										if self.cursor.fetchone()==None:
											self.cursor.execute("INSERT INTO items VALUES (%s, %s, %s, %s, %s, %s, %s)", (values[0], values[1], values[2], values[3], values[4], values[5], int(message.guild_id)))
											await channel.send("Конфигурация окончена")
										else:
											await channel.send("Такой предмет уже существует")
								await message_ed.edit(embeds=embed)
								self.connection.commit()
		except:
			pass

def setup(bot: interactions.Client, **kwargs):
	events(bot, **kwargs)