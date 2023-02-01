import hikari
from hikari import errors
import lightbulb
import logging as log
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

from canvas_bot.exceptions import NoEmbedException

job_plugin = lightbulb.Plugin("job", "To manage bot jobs")

# Update all deadline embeds on 10-minute interval
async def update_deadline() -> None:
    ds = job_plugin.app.d

    # retrieve course ids to fetch
    course_ids = ds.db.get_course_id_to_fetch()
    if not course_ids:  # no course id to fetch
        return

    # get canvas data
    assgn_data = {}
    for course_id in course_ids:
        try:
            assgn_data[course_id] = ds.canvas_api.get_upcoming_assignments(course_id)
        except ValueError as e:  # known exception: user no longer have access to a course
            log.error(e)

    # update request embeds
    all_requests = ds.db.get_all_requests()
    for guild_doc in all_requests:
        # print(guild_doc.id) # guild id
        # print(guild_doc.to_dict()['guild_name']) # guild name
        guild_req_col = guild_doc.reference.collection('guild-requests')
        for channel_doc in guild_req_col.get():
            # print(channel_doc.id) # channel id
            # print(channel_doc.to_dict()['channel_name']) # channel name
            channel_id = channel_doc.id
            channel_req_col = channel_doc.reference.collection('channel-requests')
            # print(channel_req_col)
            for msg_doc in channel_req_col.get():
                # print(msg_doc.id) # message id
                # print(msg_doc.to_dict()) # request content
                msg_id = msg_doc.id
                req = msg_doc.to_dict()
                try:
                    msg = await job_plugin.bot.rest.fetch_message(
                        channel=int(channel_id),
                        message=int(msg_id)
                    )
                    if not msg.embeds: # if embed gets removed from message
                        raise NoEmbedException()
                except (errors.NotFoundError, errors.ForbiddenError, NoEmbedException) as e:
                    msg_doc.reference.delete()  # delete request from firestore
                    ds.db.dec_course_id_to_fetch(req['course_id'])
                    if isinstance(e, NoEmbedException):
                        await msg.delete()  # delete discord msg without embed
                    continue

                if req['course_id'] not in assgn_data:
                    msg_doc.reference.delete()
                    ds.db.dec_course_id_to_fetch(req['course_id'])
                    continue

                assgn_list = []
                now = datetime.utcnow()
                for assgn in assgn_data[req['course_id']]:
                    if assgn['due_at']: 
                        due = datetime.strptime(assgn['due_at'], '%Y-%m-%dT%H:%M:%SZ') 
                        if due - now <= timedelta(days=req['due_in']):
                            assgn_list.append(assgn)
                        else:
                            break
                embed = ds.discord_embed.deadline_embed(
                    course_id=req['course_id'],
                    course_title=req['course_title'],
                    assgn_list=assgn_list,
                    due_in = req['due_in']
                )
                await msg.edit(embed=embed)
            # if channel-request subcollection is empty
            if not channel_req_col.get():
                channel_doc.reference.delete()
        # if guild-request subcollection is empty
        if not guild_req_col.get():
            guild_doc.reference.delete()

@job_plugin.listener(hikari.StartedEvent)
async def on_started(_: hikari.StartedEvent) -> None:
    ds = job_plugin.app.d
    await update_deadline()
    ds.sched.start()
    # ds.sched.add_job(update_deadline, CronTrigger(minute="*/1"))
    ds.sched.add_job(update_deadline, CronTrigger(minute="*/10"))

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(job_plugin)

# https://crontab.guru/
