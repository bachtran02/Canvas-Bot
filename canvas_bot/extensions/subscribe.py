import lightbulb
from requests import exceptions
import time

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

subscribe_plugin = lightbulb.Plugin("subscribe", "Subscribe to get notfied of new course announcement")

@subscribe_plugin.command
@lightbulb.add_checks(
    lightbulb.owner_only,
)
@lightbulb.option(
    name="course",
    description="Course to subscribe",
    required=True,
    choices=CanvasApi().get_all_active_courses('list-string'),
)
@lightbulb.command(
    name="subscribe",
    description="Subscribe to get notfied of new course announcement",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def subscribe(ctx: lightbulb.Context):
    course_id = ctx.options.course.split('-')[0].strip()
    print(course_id)

    # save channel ID, course ID

    res = await ctx.respond("Course successfully subscribed!")
    await res.delete()
    

@subscribe_plugin.set_error_handler
async def foo_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    for cause in event.exception.causes:
        if isinstance(cause, lightbulb.errors.NotOwner): # not owner exception
            await event.context.respond("Only bot owner can use this command!")

def load(bot: lightbulb.BotApp):
    bot.add_plugin(subscribe_plugin)
    