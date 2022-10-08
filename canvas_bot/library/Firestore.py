from firebase_admin import firestore

class Firestore:
    def __init__(self) -> None:
        self.db = firestore.client()
        self.col = self.db.collection('canvas-bot-db')
    
    def save_request(self, data: dict):
        self.col.add(data)

    def remove_request(self, document_id: str):
        print("Embed message inacessible!")
        print(document_id)
        self.col.document(document_id).delete() 

    def get_all_requests(self):
        return self.col.get()

    def query_watch(self, on_snapshot):
        self.col.on_snapshot(on_snapshot)
