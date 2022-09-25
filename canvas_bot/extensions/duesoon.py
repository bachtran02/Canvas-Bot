from hikari import Embed, Color
from datetime import datetime
import lightbulb

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

duesoon_plugin = lightbulb.Plugin("duesoon", "Get list of assignments due within a day")

@duesoon_plugin.command
@lightbulb.option(
    name="course",
    description="Course to follow",
    required=True,
    choices=CanvasApi().get_all_active_courses('list-string'),
)
@lightbulb.option(
    name="title",
    description="Course short name",
    required=True,
)
@lightbulb.command(
    "duesoon", "Get assignments due within a day"
)
@lightbulb.implements(lightbulb.SlashCommand)
async def duesoon(ctx: lightbulb.Context):
    course_id = ctx.options.course.split('-')[0].strip()
    course_title = ctx.options.title

    embed = DiscordEmbed().duesoon_temp_embed()
    res = await ctx.respond(embed=embed)
    msg = await res.message()
    
    Firestore().save_request({
        'course-info': {
                'course-id': course_id,
                'course-title': course_title 
            },
        'discord': {
                'channel-id': str(msg.channel_id),
                'message-id': str(msg.id),
            }
    })


def load(bot: lightbulb.BotApp):
    bot.add_plugin(duesoon_plugin)