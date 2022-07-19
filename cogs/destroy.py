import interactions
from interactions.ext.checks import guild_only
import psycopg2

class destroy(interactions.Extension):
	def __init__(self, bot, connection, cursor, **kwargs):
		self.bot = bot
		self.connection = connection
		self.cursor = cursor
	@interactions.extension_command(
		name="destroy",
		description="Удалить сделку",
		default_member_permissions=interactions.Permissions.ADMINISTRATOR,
		options=[interactions.Option(
			name="channel",
			description="Сделка которую удалить",
			type=interactions.OptionType.CHANNEL,
			required=False,
		),
	],
	)
	@guild_only()
	async def destroy(self, ctx, channel = None):
		if channel == None:
			channel = await ctx.get_channel()
		await ctx.defer()
		guild = int(ctx.guild_id)
		try:
			guild = int(ctx.guild_id)
			self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
			for row in self.cursor.fetchone():
				categ =row
				category = await interactions.get(self.bot, interactions.Channel, object_id=categ)
				category1=int(category.id)
		except:
			self.cursor.execute("UPDATE status SET status=%s, arg=%s WHERE id=%s and guild=%s", (False, 0, 3, guild))
			self.connection.commit()
		if channel.type != interactions.ChannelType.GUILD_CATEGORY:
			self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
			if self.cursor.fetchone()==None:
				await ctx.send(embeds=interactions.Embed(color=0xf50a19, description="**Категория для сделок не настроена**"))
			else:
				self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
				for row in self.cursor.fetchone():
					self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
					if row == 0:
						await ctx.send(embeds=interactions.Embed(color=0xf50a19, description="**Категория для сделок не настроена**"))
					else:
						self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (3, guild))
						for row in self.cursor.fetchone():
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
def setup(bot: interactions.Client, **kwargs):
	destroy(bot, **kwargs)