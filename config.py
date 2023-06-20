import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD = int(os.getenv("GUILD"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "3600"))
PREFIX = os.getenv("PREFIX", "!")
