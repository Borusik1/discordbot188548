import interactions
import psycopg2
from itertools import cycle
import asyncpraw
import asyncio
import random

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
					self.cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (member1, 0, 0, guild1))
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
						self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (4, guild1))
						if self.cursor.fetchone()!=None:
							self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (4, guild1))
							for row in self.cursor.fetchone():
								channel = await interactions.get(self.bot, interactions.Channel, object_id=row)
								await channel.set_nsfw(nsfw=True)
								await channel.send(embeds=embed)
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
						self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (4, guild1))
						if self.cursor.fetchone()!=None:
							self.cursor.execute("SELECT arg FROM status WHERE id=%s and guild=%s", (4, guild1))
							for row in self.cursor.fetchone():
								channel = await interactions.get(self.bot, interactions.Channel, object_id=row)
								await channel.set_nsfw(nsfw=True)
								await channel.send(embeds=embed)
								imgs.append(item.title)
			
			

	@interactions.extension_listener
	async def on_guild_member_add(self, member):
		member1 = int(member.id)
		guild = int(member.guild_id)
		self.cursor.execute("SELECT id FROM users WHERE id = %s and guild=%s;", (member1, guild))
		if self.cursor.fetchone()==None:
			self.cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (member1, 0, 0, guild))
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
def setup(bot: interactions.Client, **kwargs):
	events(bot, **kwargs)