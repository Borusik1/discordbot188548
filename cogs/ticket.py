import interactions
import psycopg2
from interactions.ext.checks import guild_only
import asyncio

class ticket(interactions.Extension):
	def __init__(self, bot, connection, cursor, **kwargs):
		self.bot = bot
		self.connection = connection
		self.cursor = cursor

	@interactions.extension_command(
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
	@guild_only()
	async def ticket(self, ctx, sub_command: str, user = None):
		member = user
		await ctx.defer()
		if sub_command=="claim":
			guild = int(ctx.guild_id)
			author = int(ctx.author.id)
			self.cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
			if self.cursor.fetchone() == None:
				self.cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
				self.connection.commit()
			else:
				pass
			self.cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
			for row in self.cursor.fetchone():
				channel = row
				try:
					channel1 = await interactions.get(self.bot, interactions.Channel, object_id=channel)
					call = channel1.id
				except:
					author = int(ctx.author.id)
					guild = int(ctx.guild_id)
					self.cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
					self.connection.commit()
			self.cursor.execute("SELECT stat FROM counter where author=%s and guild=%s", (author, guild))
			for row in self.cursor.fetchone():
				count = row
				if count==True:
					await ctx.send(embeds =interactions.Embed(description=f"**У тебя уже есть сделка <#{channel1.id}>**"))
				else:
					author = int(ctx.author.id)
					guild = int(ctx.guild_id)
					await asyncio.sleep(0.5)
					try:
						guild = int(ctx.guild_id)
						self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
						for row in self.cursor.fetchone():
							categ =row
							category = await interactions.get(self.bot, interactions.Channel, object_id=categ)
							category1=int(category.id)
					except:
						category1=None
					finally:
						author = int(ctx.author.id)
						guild1 =  await interactions.get(self.bot, interactions.Guild, object_id=int(ctx.guild_id))
						if category1:
							channel = await guild1.create_channel(name=f'сделка-{ctx.author.name}', type= interactions.ChannelType.GUILD_TEXT, parent_id=category1)
						else:
							channel = await guild1.create_channel(name=f'сделка-{ctx.author.name}', type= interactions.ChannelType.GUILD_TEXT)
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
						self.cursor.execute('UPDATE counter SET stat=%s,channel = %s where author=%s and guild=%s', (True, channel1, author, guild))
						self.connection.commit()
						await ctx.send(embeds=interactions.Embed(description=f"**Тикет <#{channel.id}> успешно создан <@{ctx.author.id}>**"))
						await channel.send(embeds=interactions.Embed(description=f"**Тикет успешно создан <@{ctx.author.id}>**"))		
		elif sub_command =="kick" or sub_command=="add":
			await ctx.get_channel()
			author = int(ctx.author.id)
			guild = int(ctx.guild_id)
			self.cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
			if self.cursor.fetchone() == None:
				self.cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
				self.connection.commit()
			self.cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
			for row in self.cursor.fetchone():
				channel1id = row
				try:
					self.cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
					for row in self.cursor.fetchone():
						channel1id = row
						guild1 = await interactions.get(self.bot, interactions.Guild, object_id=int(ctx.guild_id))
						channel1 = await interactions.get(self.bot, interactions.Channel, object_id=channel1id)
						call = channel1.id
				except:
					self.cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
					self.connection.commit()
				else:
					try:
						user= await interactions.get(self.bot, interactions.User, object_id=int(member.id))
					except:
						await ctx.send("Участника нет на сервере")
				self.cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
				for row in self.cursor.fetchone():
					if row == 0:
						await ctx.send(embeds=interactions.Embed(description=f"**У тебя нет сделок сейчас**"))
				channel1 = await interactions.get(self.bot, interactions.Channel, object_id=channel1id)
				user= await interactions.get(self.bot, interactions.User, object_id=int(member.id))
				overwrites = channel1.permission_overwrites
				if overwrites is None:
					overwrites = []
				if sub_command=="kick":
					overwrites.append(
						interactions.Overwrite(
							type=1,
							id=int(member.id),
							deny=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
						)
					)
				else:
					overwrites.append(
						interactions.Overwrite(
							type=1,
							id=int(member.id),
							allow=interactions.Permissions.VIEW_CHANNEL | interactions.Permissions.SEND_MESSAGES,
						)
					)
				await channel1.modify(permission_overwrites=overwrites)
				try:
					guild = await interactions.get(self.bot, interactions.Guild, object_id=int(ctx.guild_id))
					role = await interactions.get(self.bot, interactions.Role, guild_id = int(ctx.guild_id), object_id=936505743987867659)
					if sub_command=="kick":
						await guild.remove_member_role(role.id, member.id)
					else:
						await guild.add_member_role(role.id, member.id)
				except:
					pass
				if sub_command=="kick":
					await channel1.send(f"Прощайте <@{member.id}>.")
					await ctx.send(embeds=interactions.Embed(description=f"**Участник <@{member.id}> успешно удалён из <#{channel1.id}>.**"))
				else:
					await channel1.send(f"Здравствуйте <@{member.id}>.")
					await ctx.send(embeds=interactions.Embed(description=f"**Участник <@{member.id}> успешно добавлен в <#{channel1.id}>.**"))

		elif sub_command=="close":
			author = int(ctx.author.id)
			guild = int(ctx.guild_id)
			self.cursor.execute("SELECT author FROM counter where author=%s and guild=%s", (author, guild))
			if self.cursor.fetchone() == None:
				self.cursor.execute("INSERT INTO counter VALUES (%s, %s, %s, %s)", (False, author, 0, guild))
				self.connection.commit()
			self.cursor.execute("SELECT channel FROM counter where author=%s and guild=%s", (author, guild))
			for row in self.cursor.fetchone():
				channel1id = row
				try:
					channel1 = await interactions.get(self.bot, interactions.Channel, object_id=channel1id)
					call = channel1.id
				except:
					self.cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
					self.connection.commit()
					await ctx.send(embeds=interactions.Embed(description=f"**У тебя нет сделок**"))
				else:
					channel1 = await interactions.get(self.bot, interactions.Channel, object_id=channel1id)
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
					self.cursor.execute("UPDATE counter SET stat=%s, channel=%s where author=%s and guild=%s", (False, 0, author, guild))
					self.connection.commit()
					await ctx.send("Сделка закрыта")
					await channel1.send(embeds=interactions.Embed(description=f"**Больше создатель сделки не имеет к ней доступа**"))
def setup(bot: interactions.Client, **kwargs):
	ticket(bot, **kwargs)