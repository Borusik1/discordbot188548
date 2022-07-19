import interactions

class vip(interactions.Extension):
	def __init__(self, bot, **kwargs):
		self.bot = bot
	@interactions.extension_command(
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
	async def vip(self, ctx, sub_command: str):
		await ctx.defer()
		if sub_command == "am":
			await ctx.send(embeds=interactions.Embed(description=f"**Приватный сервер в адопте: [Нажми сюда что-бы зайти](https://www.roblox.com/games/920587237?privateServerLinkCode=41122651371977856802806669923465)**"))
		elif sub_command == "mm2":
			await ctx.send(embeds=interactions.Embed(description=f"**Приватный сервер в мардер мистери: [Нажми сюда что-бы зайти](https://www.roblox.com/games/142823291?privateServerLinkCode=89852226291968909722581151698927)**"))
		elif sub_command =="psx":
			await ctx.send(embeds=interactions.Embed(description=f"**Приватный сервер в пет симулятор X: [Нажми сюда что-бы зайти](https://www.roblox.com/games/6284583030/x3-Pet-Simulator-X?privateServerLinkCode=55975160176260713274764851250283)**"))
def setup(bot: interactions.Client, **kwargs):
	vip(bot, **kwargs)