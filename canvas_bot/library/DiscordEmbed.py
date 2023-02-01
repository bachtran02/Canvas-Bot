import os
import pytz
from canvas_bot.utils import makeBold, makeLink, toPercent, shortenCrnName
from hikari import Embed, Color
from datetime import datetime

class DiscordEmbed:
    def __init__(self) -> None:
        self.logo = os.getenv(key='CANVAS_LOGO_URL', default=None)
        self.BASE_URL = 'https://deanza.instructure.com'
        self.BASE_DISCORD_MSG_URL = 'https://discord.com/channels/'


    @staticmethod
    def create_embed(title, body):
        return Embed(
            title=title,
            description=body,
            color=Color.from_hex_code('#ff3939'),
            timestamp=datetime.now().astimezone()
        )
    
    # allcourse
    def allcourse_embed(self, course_list: list):
        body = ""
        for course in course_list:
            course_url = f"{self.BASE_URL}/courses/{course['id']}"
            body += f"{makeBold(course['id'])} - {makeLink(course['name'], course_url)}" + '\n'
            
        return self.create_embed(
            title="Course List",
            body=body,
        ).set_footer(
            text='Canvas Bot',
            icon=self.logo
        )
    
    # deadline
    def deadline_temp_embed(self):
        return self.create_embed(
            title="Request saved!",
            body="Message is waiting to be updated..."
        ).set_footer(
            text="Sent",
            icon=self.logo
        )

    def deadline_embed(self, course_title: str, course_id: str, assgn_list: list, due_in: int):
        if assgn_list:
            title = f"Due within {due_in} Day(s) | {len(assgn_list)} assignment(s)"
        else:
            title = f"No Assignment Due within {due_in} Day(s)"
            
        course_url = f"{self.BASE_URL}/courses/{course_id}"
        body = makeBold(f'Course: {makeLink(course_title, course_url)}')

        e = self.create_embed(
            title=title,
            body=body,
        ).set_footer(
            text="Last updated",
            icon=self.logo
        )

        for assgn in assgn_list:
            # due time
            tz = pytz.timezone('UTC')
            due_time = datetime.strptime(assgn['due_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=tz)
            due_stamp = int(due_time.timestamp())

            # points
            org_points = assgn['points_possible']
            points = int(org_points) if org_points.is_integer() else org_points 

            # embed field body
            body  = f"{makeBold(makeLink(assgn['name'], assgn['html_url']))}" + '\n'
            body += f"{makeBold('Points:')} `{points}`" + '\n'
            body += f"{makeBold('Due:')} <t:{due_stamp}:f> ({makeBold(f'<t:{due_stamp}:R>')})" + '\n'

            name = makeBold("Quiz" if assgn['is_quiz_assignment'] is True else "Assignment")
            e.add_field(
                name=name,
                value=body
            )
        return e

    def all_deadline_embed(self, guild_dict: dict):
        if not guild_dict:
            return self.create_embed(
                title="There is no deadline embed in the server",
                body=None
            ).set_footer(
                text='Canvas Bot',
                icon=self.logo
            )

        guild_id = guild_dict['guild_id']
        # format: base_url/{guild_id}/{channel_id}/{message_id}
        e = self.create_embed(
            title=f"All deadline embeds in {guild_dict['guild_name']}",
            body=None,
        ).set_footer(
            text='Canvas Bot',
            icon=self.logo
        )

        for channel_dict in guild_dict['guild_requests']:
            channel_id = channel_dict['channel_id']
            body_str = ""
            for message_dict in channel_dict['channel_requests']:
                msg_id = message_dict['message_id']
                body_str += makeLink(
                    string=f"{message_dict['course_title']}-{message_dict['due_in']}d",
                    link=f"{self.BASE_DISCORD_MSG_URL}{guild_id}/{channel_id}/{msg_id}"
                ) + '\n'
            e.add_field(
                name=channel_dict['channel_name'],
                value=body_str,
                inline=True,
            )
        return e
    
    def course_roster_embed(self, course_info: list, roster_search: list, query: str):
        
        course_url = f"{self.BASE_URL}/courses/{course_info[0]}"
        body = f"Course: {makeLink(makeBold(shortenCrnName(course_info[1])), course_url)}\n"

        if not query:
            
            body += f"Student Count: {makeBold(len(roster_search))}\n"
            body += '```'
            i = 0
            for user in roster_search:
                if not i % 2:  # 2 entries per row
                    body += '\n' 
                body += '{:<25}'.format(user['name']) + '\t'
                i += 1
            body += "```"

            return self.create_embed(
                title=f"Course Roster",
                body=body,
            ).set_footer(
                text='Canvas Bot',
                icon=self.logo
            )
    
        body += f"Search query: {makeBold(query)}\n"
        body += f"Search result: {makeBold(len(roster_search))}\n\n"

        e = self.create_embed(
            title=f"Course Roster",
            body=body,
        ).set_footer(
            text='Canvas Bot',
            icon=self.logo
        )

        i = 0
        for user in roster_search:
            
            canvas_url = f"{self.BASE_URL}/courses/{course_info[0]}/users/{user['id']}"
            
            dt = datetime.strptime(user['created_at'], '%Y-%m-%dT%H:%M:%S%z')
            ts = int(dt.timestamp())
            
            body = f"Canvas ID: {makeLink(makeBold(user['id']), canvas_url)}\n"
            body += f"Display name: {makeBold(user['name'])}\n"
            body += f"Sortable name: {makeBold(user['sortable_name'])}\n"
            body += f"Created: <t:{ts}:d> (<t:{ts}:R>)"

            e.add_field(
                name=user['name'],
                value=body,
                inline=True,
            )

            # if search query exists then limits to first 10 results
            i += 1
            if i >= 10:
                break
            
        return e

    def assignment_stats_embed(self, course_info: list, assgn_list: list):
        
        shortenCrnName(course_info[1])

        course_url = f"{self.BASE_URL}/courses/{course_info[0]}"
        body = f"Course: {makeLink(makeBold(shortenCrnName(course_info[1])), course_url)}\n"

        e = self.create_embed(
            title=f"Assignment Stats",
            body=body,
        ).set_footer(
            text='Canvas Bot',
            icon=self.logo
        )

        cnt_stats = 0
        for assgn in assgn_list:
            if 'score_statistics' not in assgn:
                continue
            
            cnt_stats += 1
            
            # points
            org_points = assgn['points_possible']
            points = int(org_points) if org_points.is_integer() else org_points
            stats = assgn['score_statistics']

            # embed field body
            body  = f"{makeBold(makeLink(assgn['name'], assgn['html_url']))}\n"
            body += "```"

            body += f"Points: {points}" + '\n'
            body += '{:<20}'.format(f"Max: {stats['max']} ({toPercent(stats['max'], points)}%)") + '\t'
            body += f"Average: {stats['mean']} ({toPercent(stats['mean'], points)}%)" + '\n'
            body += '{:<20}'.format(f"Min: {stats['min']} ({toPercent(stats['min'], points)}%)") + '\t'
            body += f"Median:  {stats['median']} ({toPercent(stats['median'], points)}%)" + '\n'

            # quartile
            # body += '{:<25}'.format(f"Upper Quartile: {stats['upper_q']} ({toPercent(stats['upper_q'], points)}%)") + '\t'
            # body += '{:<25}'.format(f"Lower Quartile: {stats['lower_q']} ({toPercent(stats['lower_q'], points)}%)") + '\n'

            body += "```"

            name = makeBold("Quiz Stats" if assgn['is_quiz_assignment'] is True else "Assignment Stats")
            e.add_field(
                name=name,
                value=body
            )

        if not cnt_stats:
            e.add_field(
                name="No Stats found!",
                value="Grade Statistics not exist or hidden by instructor"
            )

        return e