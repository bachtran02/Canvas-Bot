from firebase_admin import firestore

class Firestore:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.col = self.db.collection('canvas-bot-db')
        # manage number of requests in one channel/server
        self.admin = self.db.collection('canvas-bot-admin').document('deadline-admin')

        self.check_exist()

    def check_exist(self):
        # if doc doesn't exist
        if not self.admin.get()._exists:
            self.admin.set({
                '0000': 0,  # set dummy datapoint
            })
    
    def save_request(self, data: dict):
        if self.check_valid(data['discord']):
            self.col.add(data)
            return True
        return False

    def remove_request(self, document_id: str, ids: dict):
        self.col.document(document_id).delete()
        self.admin.update({
            f"{ids['server-id']}.req_num": firestore.Increment(-1),
            f"{ids['server-id']}.{ids['channel-id']}.req_num": firestore.Increment(-1),
            f"{ids['server-id']}.{ids['channel-id']}.message_ids":  firestore.ArrayRemove([ids['message-id']])
        })
        doc = self.admin.get().to_dict()
        if ids['server-id'] in doc and doc[ids['server-id']]['req_num'] <= 0:
            self.admin.update({
                ids['server-id']: firestore.DELETE_FIELD
            })
            return
        if ids['channel-id'] in doc['server-id'] and doc[ids['server-id']]['channel_id']['req_num'] <= 0:
            self.admin.update({
                f"{ids['server-id']}.{ids['channel-id']}": firestore.DELETE_FIELD
            })

    def get_all_requests(self):
        return self.col.get()

    # def query_watch(self, on_snapshot):
    #     self.col.on_snapshot(on_snapshot)

    # keep track of number requests in channel (will add server too)
    def check_valid(self, ids: dict):
        # TODO: set limit for number of requests in channel/server
        self.admin.update({
            f"{ids['server-id']}.req_num": firestore.Increment(1),
            f"{ids['server-id']}.{ids['channel-id']}.req_num": firestore.Increment(1),
            f"{ids['server-id']}.{ids['channel-id']}.message_ids":  firestore.ArrayUnion([ids['message-id']])
        })
        return True

    # TODO: error if get all when no document exists
    def get_server_requests(self, guild_id: str):
        doc = self.admin.get().to_dict()
        if len(doc) == 0 or len(doc) == 1:  # empty or only contain dummy datapoint
            return []
        print(doc.get(guild_id, []))
