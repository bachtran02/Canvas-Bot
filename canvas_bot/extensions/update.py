import hikari
import lightbulb
from apscheduler.triggers.cron import CronTrigger

from firebase_admin import firestore

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

update_plugin = lightbulb.Plugin("Update", "Update all assignment embed instances on interval")

async def update_embeds() -> None:
    all_reqs = Firestore().get_all_requests()
    for req in all_reqs:
        req = req.to_dict()
        msg = await update_plugin.bot.rest.fetch_message(
            channel=int(req['discord']['channel-id']),
            message=int(req['discord']['message-id'])
        )

        assgn_list = CanvasApi().get_due_within_day(req['course-info']['course-id'])
        embed = DiscordEmbed().duesoon_embed(
            course_id=req['course-info']['course-id'],
            course_title=req['course-info']['course-title'],
            assgn_list=assgn_list
        )
        await msg.edit(embed=embed)

# def on_snapshot(col_snapshot, changes, read_time):
#     for change in changes:
#         if change.type.name == 'ADDED':
#             print(f'New req: {change.document.id}')
#             print(change.document.to_dict())

@update_plugin.listener(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    update_plugin.app.d.sched.add_job(update_embeds, CronTrigger(minute="*/10"))
    
    # initiate Firestore query-watch for new requests
    # Firestore().query_watch(on_snapshot)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(update_plugin)