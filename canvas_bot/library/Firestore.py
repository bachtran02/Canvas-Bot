from firebase_admin import firestore

class Firestore:
    def __init__(self) -> None:
        self.db = firestore.client()
    
    def save_request(self, data: dict):
        self.db.collection('canvas-bot-db').add(data)

    def get_all_requests(self):
        return self.db.collection('canvas-bot-db').get()