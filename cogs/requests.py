import interactions
from interactions.ext.checks import guild_only
from interactions.ext.enhanced import cooldown
import psycopg2
import calendar, time
import datetime

button = interactions.Button(
		style=interactions.ButtonStyle.PRIMARY,
		label="Нужна сделка",
		custom_id="request"
)

async def cooldown_error_form(ctx, amount):
	t = amount.total_seconds()
	a = int(str(time.time()).split('.')[0])
	b = int(str(t).split('.')[0])
	timestamps = a+b
	await ctx.send(f"Ты уже отправил запрос, <t:{timestamps}:R> сможешь опять.", ephemeral=True)

class requests(interactions.Extension):
	def __init__(self, bot, connection, cursor, **kwargs):
		self.bot = bot
		self.connection = connection
		self.cursor = cursor

	@interactions.extension_command(
	    name="setup",
	    description="Установить запрос на сделки",
		default_member_permissions=interactions.Permissions.ADMINISTRATOR,
	)
	@guild_only()
	async def setup(self, ctx):
		await ctx.defer()
		self.cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (2, int(ctx.guild_id)))
		if self.cursor.fetchone() is None:
			await ctx.send("Не настроен канал для получения запросов", ephemeral=True)
		else:
			self.cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (2, int(ctx.guild_id)))
			for row in self.cursor.fetchone():
				if row == False:
					await ctx.send("Информация о канале для запросов устарела", ephemeral=True)
				else:
					await ctx.send(embeds=interactions.Embed(description="**Создать запрос на сделку**"), components=button)

	@interactions.extension_component("request")
	async def button_response(self, ctx):
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

	@interactions.extension_modal("request_form")
	@cooldown(seconds=600, error=cooldown_error_form, type="user")
	async def modal_response(self, ctx, response = str, response2 = str, response3 = None):
		await ctx.defer(ephemeral=True)
		try:
			m_id=int(response)
			member = await interactions.get(self.bot, interactions.User, object_id=m_id)
			print(member)
		except:
			await ctx.send(f"Неверно указан ID", ephemeral=True)
		else:
			if int(response) == int(ctx.author.id):
				await ctx.send(f"Нельзя указать себя", ephemeral=True)
			else:
				author = int(ctx.author.id)
				guild = await interactions.get(self.bot, interactions.Guild, object_id=int(ctx.guild_id))
				guild1 = int(guild.id)
				self.cursor.execute("SELECT arg FROM status where id=%s and guild=%s", (2, guild1))
				for row in self.cursor.fetchone():
					channel = row
					try:
						channel1 = await interactions.get(self.bot, interactions.Channel, object_id=channel)
						call = channel1.id
					except:
						author = int(ctx.author.id)
						guild = int(ctx.guild_id)
						self.cursor.execute("UPDATE status SET status=%s, arg=%s where id=%s and guild=%s", (False, 0, 2, guild))
						self.connection.commit()
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
						self.cursor.execute("SELECT status FROM status WHERE id=%s and guild=%s", (2, int(ctx.guild_id)))
						for row in self.cursor.fetchone():
							if row == False:
								await ctx.send(f"Информация о канале для получения форм устарела. Пожалуйста, сообщите администраторам")
							else:
								await channel1.send(embeds=embed)
								await ctx.send(f"Форма успешно отправлена")
def setup(bot: interactions.Client, **kwargs):
	requests(bot, **kwargs)