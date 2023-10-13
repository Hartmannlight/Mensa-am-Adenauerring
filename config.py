import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

GUILD = int(os.getenv("GUILD"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "3600"))
