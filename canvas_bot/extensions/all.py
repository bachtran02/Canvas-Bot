import lightbulb

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

course_plugin = lightbulb.Plugin("all", 'Get all assignment embeds in server')

@course_plugin.command
@lightbulb.command(
    "all", 'Get all assignment embeds in server'
)
@lightbulb.implements(lightbulb.SlashCommand)
async def all(ctx: lightbulb.Context):
    guild_id = ctx.guild_id  # get server id
    guild_all_reqs = Firestore().get_guild_requests(str(guild_id))
    
    embed = DiscordEmbed().all_embed(guild_all_reqs)
    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp):
    bot.add_plugin(course_plugin)