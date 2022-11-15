import lightbulb

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

course_plugin = lightbulb.Plugin("course list", 'Get list of courses marked as "favorite" on your Canvas profile')

@course_plugin.command
@lightbulb.command(
    "courselist", 'Get list of courses marked as "favorite" on your Canvas profile'
)
@lightbulb.implements(lightbulb.SlashCommand)
async def courselist(ctx: lightbulb.Context):
    course_list = CanvasApi().get_all_active_courses('list-dict')
    embed = DiscordEmbed().courselist_embed(course_list)
    await ctx.respond(embed=embed)
    

def load(bot: lightbulb.BotApp):
    bot.add_plugin(course_plugin)