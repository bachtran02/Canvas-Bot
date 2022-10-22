import os
import lightbulb
import hikari
from hikari import Intents

bot = lightbulb.BotApp(
    token= os.environ.get("DISCORD_TOKEN"),
    help_slash_command=True,
    intents=(Intents.GUILDS | Intents.GUILD_MESSAGES)
)

extensions = ['deadline', 'update']  # 'courselist'
for ext in extensions:
    bot.load_extensions(f"canvas_bot.extensions.{ext}")

def run():
    bot.run()

# global error logger
@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(err_event: lightbulb.CommandErrorEvent) -> None:
    ctx = err_event.context
    channel = ctx.get_channel()
    guild = ctx.get_guild()

    print("-------------Error--------------")
    print(f"Author: {ctx.author}")
    print(f'Command: "{ctx.command.name}"')
    print(f'Error message: "{err_event.exception}"')
    print(f'Server: name="{guild.name}", id={guild.id}')
    print(f'Channel: name="{channel.name}", id={channel.id}')
    print("---------------------------------")
