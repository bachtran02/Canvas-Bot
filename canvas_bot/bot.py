import hikari
from hikari import Intents
import lightbulb
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = lightbulb.BotApp(
    token= os.environ.get("DISCORD_TOKEN"),
    help_slash_command=True,
    intents=(Intents.GUILDS | Intents.GUILD_MESSAGES)
)

bot.d.sched = AsyncIOScheduler()
bot.d.sched.start()

extensions = ['courselist', 'duesoon', 'update']
for ext in extensions:
    bot.load_extensions(f"canvas_bot.extensions.{ext}")

def run():
    bot.run()