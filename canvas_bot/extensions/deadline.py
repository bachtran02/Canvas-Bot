import lightbulb
from requests import exceptions

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed
from canvas_bot.Utils import buildDeadlineChoices

deadline_plugin = lightbulb.Plugin("deadline", "Get self-updated upcoming deadline embed")

@deadline_plugin.command
@lightbulb.add_checks(
    # lightbulb.owner_only,
    # lightbulb.has_channel_permissions(
    # Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES)
)
@lightbulb.option(
    name="course",
    description="Course to follow",
    required=True,
    choices=buildDeadlineChoices(CanvasApi().get_all_active_courses()),
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
    default=1  # maximum 14 days
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

    Firestore().save_request(
        ctx.get_guild(),
        ctx.get_channel(),{
        'course_id': course_id,
        'course_title': course_title,
        'due_in': due_in,
        'message_id': str(msg.id),
    })

# @deadline.set_error_handler
# async def foo_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
#     for cause in event.exception.causes:
#         if isinstance(cause, lightbulb.errors.NotOwner): # not owner exception
#             await event.context.respond("Only bot owner can use this command!")
        

@deadline.set_error_handler
async def foo_error_handler(event) -> bool:
    print(event)

def load(bot: lightbulb.BotApp):
    bot.add_plugin(deadline_plugin)
    