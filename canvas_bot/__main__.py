import os
from canvas_bot import bot
from hikari import errors
import firebase_admin
from firebase_admin import credentials

if __name__ == "__main__":
    try:
        # initiate Firebase app
        cred = credentials.Certificate(os.environ.get('FIRESTORE_KEY_PATH'))
        firebase_admin.initialize_app(cred)
        # run Discord bot instance
        bot.run()
        
    except PermissionError:
        print("Error - Invalid key/path to key for Firebase app")
    except errors.UnauthorizedError:
        print("Error - Invalid Bot Token")
    