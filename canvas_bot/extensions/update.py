import hikari
from hikari import errors
import lightbulb
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from canvas_bot.library.Firestore import Firestore
from canvas_bot.library.CanvasApi import CanvasApi
from canvas_bot.library.DiscordEmbed import DiscordEmbed

from canvas_bot.Utils import NoEmbedException

update_plugin = lightbulb.Plugin("update", "Update all assignment embed instances on interval")

async def update_embeds() -> None:
    all_reqs = Firestore().get_all_requests()
    for req in all_reqs:
        req_id = req.id # get document ID
        req_data = req.to_dict() # get document content
        due_in = req_data['due-in']
        discord_ids = req_data['discord']
        try:
            msg = await update_plugin.bot.rest.fetch_message(
                channel=int(discord_ids['channel-id']),
                message=int(discord_ids['message-id'])
            )
            if not msg.embeds: # if embed gets removed from message
                raise NoEmbedException()
        except NoEmbedException:
            await msg.delete() # delete message without embed
            Firestore().remove_request(req_id, discord_ids) # remove entry from firestore
            continue
        except (errors.NotFoundError, errors.ForbiddenError, NoEmbedException):
            Firestore().remove_request(req_id, discord_ids) # remove entry from firestore
            continue

        assgn_list = CanvasApi().get_due_in(req_data['course-info']['course-id'], due_in)
        embed = DiscordEmbed().deadline_embed(
            course_id=req_data['course-info']['course-id'],
            course_title=req_data['course-info']['course-title'],
            assgn_list=assgn_list,
            due_in = due_in
        )

        await msg.edit(embed=embed)

async def post_announcement() -> None:
    # check for new announcements
    # if announcement != current_id -> new announcement
    #   push announcement to server
    # else return
    # get webhook URL (pair<URL - course id)


    pass

@update_plugin.listener(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    update_plugin.app.d.sched = AsyncIOScheduler()
    update_plugin.app.d.sched.start()
    update_plugin.app.d.sched.add_job(update_embeds, CronTrigger(minute="*/1"))

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(update_plugin)

# https://crontab.guru/
