import interactions
from interactions.ext.checks import guild_only
import psycopg2

class set(interactions.Extension):
	def __init__(self, bot, connection, cursor, **kwargs):
		self.bot = bot
		self.connection = connection
		self.cursor = cursor

	@interactions.extension_command(
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
			
		],
	)
	@guild_only()
	async def cmd(self, ctx, sub_command: str, channel = None, category = None):
		await ctx.defer()
		guild = int(ctx.guild_id)
		if sub_command=="channel":
			channel1 = int(channel.id)
			if channel.type == interactions.ChannelType.GUILD_TEXT:
				self.cursor.execute("SELECT id FROM status where id=%s and guild=%s", (1, guild))
				if self.cursor.fetchone()==None:
					self.cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (1, True, channel1, guild))
				else:
					self.cursor.execute('UPDATE status SET arg=%s where id=%s and guild=%s', (channel1, 1, guild))
				self.connection.commit()
				embed=interactions.Embed(color =0x2ecc71, description=f"Приветственный канал успешно настроен на <#{channel1}>")
				await ctx.send(embeds=embed)
			else:
				embed=interactions.Embed(color =0xf50a19, description=f"Это не текстовый канал")
				await ctx.send(embeds=embed)
		elif sub_command=="category":
			if category.type == interactions.ChannelType.GUILD_CATEGORY:
				category1 = int(category.id)
				self.cursor.execute("SELECT id FROM status where id=%s and guild=%s", (3, guild))
				if self.cursor.fetchone()==None:
					self.cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (3, True, category1, guild))
				else:
					self.cursor.execute('UPDATE status SET arg=%s where id=%s and guild=%s', (category1, 3, guild))
				self.connection.commit()
				embed=interactions.Embed(color =0x2ecc71, description=f"Категория для тикетов успешно настроена на **{category.name}**")
				await ctx.send(embeds=embed)
			else:
				embed=interactions.Embed(color =0xf50a19, description=f"Это не категория")
				await ctx.send(embeds=embed)
		elif sub_command=="requests":
			channel1 = int(channel.id)
			if channel.type == interactions.ChannelType.GUILD_TEXT:
				self.cursor.execute("SELECT id FROM status where id=%s and guild=%s", (2, guild))
				if self.cursor.fetchone()==None:
					self.cursor.execute("INSERT INTO status VALUES (%s, %s, %s, %s)", (2, True, channel1, guild))
				else:
					self.cursor.execute('UPDATE status SET arg=%s, status=%s where id=%s and guild=%s', (channel1, True,  2, guild))
				self.connection.commit()
				await ctx.send(embeds=interactions.Embed(color=0x14e34b, description=f"Канал для получения запросов успешно настроен на {channel.mention}"))
			else:
				await ctx.send("Канал не текствого типа")
def setup(bot: interactions.Client, **kwargs):
	set(bot, **kwargs)
