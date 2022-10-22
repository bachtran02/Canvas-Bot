import hikari
from hikari import errors
import lightbulb
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

from canvas_bot.Utils import NoEmbedException

update_plugin = lightbulb.Plugin("Update", "Update all assignment embed instances on interval")

async def update_embeds() -> None:
    all_reqs = Firestore().get_all_requests()
    for req in all_reqs:
        req_id = req.id # get document ID
        req_data = req.to_dict() # get document content
        due_in = req_data['due-in']
        try:
            msg = await update_plugin.bot.rest.fetch_message(
                channel=int(req_data['discord']['channel-id']),
                message=int(req_data['discord']['message-id'])
            )
            if not msg.embeds: # if embed gets removed from message
                raise NoEmbedException()
        except NoEmbedException:
            await msg.delete() # delete message without embed
            Firestore().remove_request(req_id) # remove entry from firestore
            continue
        except (errors.NotFoundError, errors.ForbiddenError, NoEmbedException):
            Firestore().remove_request(req_id) # remove entry from firestore
            continue

        assgn_list = CanvasApi().get_due_in(req_data['course-info']['course-id'], due_in)
        embed = DiscordEmbed().deadline_embed(
            course_id=req_data['course-info']['course-id'],
            course_title=req_data['course-info']['course-title'],
            assgn_list=assgn_list,
            due_in = due_in
        )

        await msg.edit(embed=embed)


# @syncer
# async def update_on_new_req():
#     msg = await update_plugin.bot.rest.fetch_message(
#                 channel=int(req['discord']['channel-id']),
#                 message=int(req['discord']['message-id'])
#             )
#     pass


# def on_snapshot(col_snapshot, changes, read_time):
#     print("Number of changes:", len(changes))
#     for change in changes:
#         if change.type.name == 'ADDED':
#             print(f'New req: {change.document.id}')
#             print(change.document.to_dict())

@update_plugin.listener(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    update_plugin.app.d.sched = AsyncIOScheduler()
    update_plugin.app.d.sched.start()
    update_plugin.app.d.sched.add_job(update_embeds, CronTrigger(minute="*/1"))


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(update_plugin)

# https://crontab.guru/