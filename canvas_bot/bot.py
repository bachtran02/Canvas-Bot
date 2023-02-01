import os
import logging as log
import lightbulb
import hikari
from hikari import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

import firebase_admin
from firebase_admin import firestore

bot = lightbulb.BotApp(
    token=os.environ.get("DISCORD_TOKEN"),
    help_slash_command=False,
    intents=(Intents.GUILDS | Intents.GUILD_MESSAGES),
    banner=None,
)

for ext in ['deadline', 'jobs', 'commands']:
    bot.load_extensions(f"canvas_bot.extensions.{ext}")

@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    log.info("Bot is starting...")
    # add objects to bot for usage in plugins
    
    bot.d.db = Firestore(firestore.client())
    bot.d.discord_embed = DiscordEmbed()
    bot.d.canvas_api = CanvasApi()
    bot.d.sched = AsyncIOScheduler()

@bot.listen(hikari.StoppingEvent)
async def on_stopping(_: hikari.StoppingEvent) -> None:
    app = firebase_admin.get_app()
    firebase_admin.delete_app(app=app)
    bot.d.sched.shutdown()

@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(err_event: lightbulb.CommandErrorEvent) -> None:
    ctx = err_event.context
    channel = ctx.get_channel()
    guild = ctx.get_guild()

    log.error("-------------Error--------------")
    log.error(f"Author: {ctx.author}")
    log.error(f'Command: "{ctx.command.name}"')
    log.error(f'Error message: "{err_event.exception}"')
    log.error(f'Server: name="{guild.name}", id={guild.id}')
    log.error(f'Channel: name="{channel.name}", id={channel.id}')
    log.error("---------------------------------")

    await ctx.respond("Error while running command!")

def run():
    bot.run()
