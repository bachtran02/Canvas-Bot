import lightbulb
from hikari import Permissions

from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.utils import buildDeadlineChoices

deadline_plugin = lightbulb.Plugin("deadline", "Get self-updated upcoming-deadline embed")

@deadline_plugin.command
@lightbulb.add_checks(
    lightbulb.owner_only,
    lightbulb.guild_only,
    lightbulb.has_channel_permissions(
        Permissions.VIEW_CHANNEL | 
        Permissions.SEND_MESSAGES
    )
)
@lightbulb.option(
    name="course",
    description="Course to follow",
    required=True,
    choices=buildDeadlineChoices(CanvasApi().get_favorite_courses()),
)
@lightbulb.option(
    name="title",
    description="Course title (e.g: CIS 22C, Math 22)",
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
    ds = deadline_plugin.app.d

    course_id = ctx.options.course.split('-')[0].strip()
    course_title = ctx.options.title
    due_in = min(int(ctx.options.due_in), 14)


    embed = ds.discord_embed.deadline_temp_embed()
    res = await ctx.respond(embed=embed)
    msg = await res.message()

    ds.db.save_request(
        ctx.get_guild(),
        ctx.get_channel(),{
        'course_id': course_id,
        'course_title': course_title,
        'due_in': due_in,
        'message_id': str(msg.id),
    })

@deadline_plugin.command
@lightbulb.command(
    "all_deadline", 'Get all auto-updated assignment embeds in server'
)
@lightbulb.implements(lightbulb.SlashCommand)
async def all_deadline(ctx: lightbulb.Context):
    ds = deadline_plugin.app.d
    guild_id = ctx.guild_id  # get server id
    guild_all_reqs = ds.db.get_guild_requests(str(guild_id))
    
    embed = ds.discord_embed.all_deadline_embed(guild_all_reqs)
    await ctx.respond(embed=embed)

@deadline_plugin.set_error_handler
async def foo_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f"Something went wrong during invocation of command `{event.context.command.name}`.")
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("Only bot owner can use this command!")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.")

def load(bot: lightbulb.BotApp):
    bot.add_plugin(deadline_plugin)
    