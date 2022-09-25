import dotenv
import firebase_admin
from firebase_admin import credentials

# load .env credentials
dotenv.load_dotenv("secrets/.env")

# initiate Firebase app
cred = credentials.Certificate("secrets/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
