from hikari import Embed, Color, Permissions
from datetime import datetime
import lightbulb

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

deadline_plugin = lightbulb.Plugin("deadline", "Get list of assignments due within a day")

@deadline_plugin.command
@lightbulb.add_checks(
    lightbulb.owner_only,
    # lightbulb.has_channel_permissions(Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES)
)
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
@lightbulb.option(
    name="due_in",
    description="Assignments due within the next given number of days",
    required=False,
    default=1
)
@lightbulb.command(
    name="deadline",
    description="Get upcoming deadlines",
)
@lightbulb.implements(lightbulb.SlashCommand)
async def deadline(ctx: lightbulb.Context):
    course_id = ctx.options.course.split('-')[0].strip()
    course_title = ctx.options.title
    due_in = int(ctx.options.due_in)

    embed = DiscordEmbed().deadline_temp_embed()
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
        },
        'due-in': due_in
    }, msg.channel_id)

@deadline.set_error_handler
async def foo_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    for cause in event.exception.causes:
        if isinstance(cause, lightbulb.errors.NotOwner): # not owner exception
            await event.context.respond("Only bot owner can use this command!")

def load(bot: lightbulb.BotApp):
    bot.add_plugin(deadline_plugin)