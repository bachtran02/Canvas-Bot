from firebase_admin import firestore

class Firestore:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.col = self.db.collection('canvas-bot-db')
        # manage number of requests in one channel/server
        self.admin = self.db.collection('canvas-bot-admin').document('admin')
    
    def save_request(self, data: dict, channel_id: str):
        if self.check_valid(channel_id):
            self.col.add(data)
            return True
        return False

    def remove_request(self, document_id: str, channel_id: str):
        self.col.document(document_id).delete()
        self.admin.update({
            channel_id: firestore.Increment(-1),
        })
        # if value is 0 remove field from document
        data = self.admin.get()._data
        if channel_id in data and data[channel_id] == 0:
            self.admin.update({
                channel_id: firestore.DELETE_FIELD
            })

    def get_all_requests(self):
        return self.col.get()

    def query_watch(self, on_snapshot):
        self.col.on_snapshot(on_snapshot)

    # keep track of number requests in channel (will add server too)
    def check_valid(self, channel_id: str):
        # if doc doesn't exist
        if not self.admin.get()._exists:
            self.admin.set({
                '0000': 0,  # container datapoint
            })
        self.admin.update({
            channel_id: firestore.Increment(1),
        })
        
        # TODO: set limit for number of requests in channel/server

        return True
