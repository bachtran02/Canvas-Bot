import os
import logging as log
from canvas_bot import bot
from hikari import errors

import firebase_admin
from firebase_admin import credentials

if __name__ == "__main__":
    try:
        # initializes and returns a new Firebase app instance
        cred = credentials.Certificate(os.environ.get('FIRESTORE_KEY_PATH'))
        firebase_admin.initialize_app(cred)
        
        bot.run()  # run Discord bot instance
    except (PermissionError, FileNotFoundError):
        log.error("Invalid key/path to key for Firebase app")
    except errors.UnauthorizedError:
        log.error("Invalid Bot Token")
    
