from firebase_admin import firestore
import hikari

class Firestore:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.req = self.db.collection('request-database')
        self.course_to_fetch_col = self.db.collection('course-to-fetch')

    def inc_course_id_to_fetch(self, course_id: str):
        doc = self.course_to_fetch_col.document(str(course_id))
        if doc.get().exists:
            doc.update({ 'num_requests': firestore.Increment(1) })
        else:
            doc.set({ 'num_requests': 1 })

    def dec_course_id_to_fetch(self, course_id: str):
        doc = self.course_to_fetch_col.document(str(course_id))
        doc.update({ 'num_requests': firestore.Increment(-1) })
        if doc.get().to_dict()['num_requests'] == 0:
            doc.delete()

    def get_course_id_to_fetch(self):
        id_list = []
        doc_list = self.course_to_fetch_col.list_documents()
        for doc in doc_list:
            id_list.append(doc.id)
        return id_list

    def save_request(self, guild:hikari.Guild, channel: hikari.GuildChannel, req: dict):
        self.inc_course_id_to_fetch(req['course_id'])
        guild_doc = self.req.document(str(guild.id))
        if not guild_doc.get().exists:
            guild_doc.set({'guild_name': guild.name})
        channel_doc = guild_doc.collection('guild-requests').document(str(channel.id))
        if not channel_doc.get().exists:
            channel_doc.set({'channel_name': channel.name})
        message_doc = channel_doc.collection('channel-requests').document(req['message_id'])
        message_doc.set(req)

    def get_all_requests(self):
        return self.req.stream()

    def get_guild_requests(self, guild_id: str):
        guild_doc = self.req.document(guild_id)
        if not guild_doc.get().exists:
            return {}
        # construct response dict
        guild_dict = guild_doc.get().to_dict()  # only has guild name
        guild_dict['guild_id'] = guild_doc.id
        guild_req_col = guild_doc.collection('guild-requests')
        guild_req = []
        for channel_doc in guild_req_col.get():
            channel_id = channel_doc.id
            channel_dict = channel_doc.reference.get().to_dict()
            channel_dict['channel_id'] = channel_id
            channel_req_col = channel_doc.reference.collection('channel-requests')
            channel_req = []
            for msg_doc in channel_req_col.get():
                msg_dict = {}
                msg_dict['message_id'] = msg_doc.id
                msg_dict['title'] = msg_doc.to_dict()['course_title']
                channel_req.append(msg_dict)
            channel_dict['channel_requests'] = channel_req
            guild_req.append(channel_dict)
        guild_dict['guild_requests'] = guild_req

        return guild_dict



