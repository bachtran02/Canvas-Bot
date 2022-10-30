import os
import dotenv
import firebase_admin
from firebase_admin import credentials

# load .env credentials
dotenv.load_dotenv("secrets/.env")

# initiate Firebase app
cred = credentials.Certificate(os.environ.get('FIRESTORE_KEY_PATH'))
firebase_admin.initialize_app(cred)
