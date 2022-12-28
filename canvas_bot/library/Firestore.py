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
        db_doc = self.req.document(str(guild.id))
        if not db_doc.get().exists:
            db_doc.set({'guild_name': guild.name})
        guild_doc = db_doc.collection('guild-requests').document(str(channel.id))
        if not guild_doc.get().exists:
            guild_doc.set({'channel_name': channel.name})
        channel_doc = guild_doc.collection('channel-requests').document(req['message_id'])
        channel_doc.set(req)

    def get_all_requests(self):
        return self.req.stream()

