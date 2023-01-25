import lightbulb
from hikari import Permissions

from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.utils import buildDeadlineChoices

commands_plugin = lightbulb.Plugin("allcourse", 'Get list of courses marked as "favorite" on your Canvas account')

@commands_plugin.command
@lightbulb.add_checks(
    lightbulb.owner_only,
    lightbulb.has_channel_permissions(
    Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES)
)
@lightbulb.command(
    "allcourse", 'Get list of courses marked as "favorite" on your Canvas account'
)
@lightbulb.implements(lightbulb.SlashCommand)
async def allcourse(ctx: lightbulb.Context):
    ds = commands_plugin.app.d
    course_list = ds.canvas_api.get_favorite_courses()
    embed = ds.discord_embed.allcourse_embed(course_list)
    await ctx.respond(embed=embed)

@commands_plugin.command
@lightbulb.add_checks(
    lightbulb.has_channel_permissions(
    Permissions.VIEW_CHANNEL | Permissions.SEND_MESSAGES)
)
@lightbulb.option(
    name="course",
    description="Course to get roster",
    required=True,
    choices=buildDeadlineChoices(CanvasApi().get_favorite_courses()),
)
@lightbulb.option(
    name="search_query", 
    description="Partial name or ID of desired user",
    required=False,
    default="",
    modifier=lightbulb.OptionModifier.CONSUME_REST
)
@lightbulb.command(
    "roster", "Get course's roster"
)
@lightbulb.implements(lightbulb.SlashCommand)
async def course_roster(ctx: lightbulb.Context):
    ds = commands_plugin.app.d
    
    course_info = [x.strip() for x in ctx.options.course.split('-')]
    query = ctx.options.search_query,

    roster_search = ds.canvas_api.get_course_roster(course_info[0], query[0])
    embed = ds.discord_embed.course_roster_embed(course_info, roster_search, query[0])
    await ctx.respond(embed=embed) 


@commands_plugin.set_error_handler
async def foo_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`.")
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("Only bot owner can use this command!")

def load(bot: lightbulb.BotApp):
    bot.add_plugin(commands_plugin)