import os
import dotenv

ENV_KEYS = ['DISCORD_TOKEN', 'FIRESTORE_KEY_PATH', 'CANVAS_TOKEN']

# load .env credentials
dotenv.load_dotenv("secrets/.env")

for key in ENV_KEYS:
    if key not in os.environ:
        raise Exception("Missing key in .env!")
