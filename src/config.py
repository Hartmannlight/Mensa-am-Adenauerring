import os
from logging.config import dictConfig
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

GUILD = int(os.getenv("GUILD"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "3600"))

GIT_HASH = os.getenv("GIT_HASH", "This feature only works when the bot is deployed via Docker image from GitHub.")


LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "[%(asctime)-19.19s - %(levelname)-8s] %(message)s"
        }
    },

    "handlers": {
        "discord_py_console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },

        "discord_py_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "discord_py.log",
            "mode": "a",
            "formatter": "standard"
        },

        "bot_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },

        "bot_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "mensa_bot.log",
            "mode": "a",
            "formatter": "standard"
        }
    },

    "loggers": {
        "bot": {
            "handlers": ["bot_console", "bot_file"],
            "level": "DEBUG",
            "propagate": False
        },

        "discord": {
            "handlers": ["discord_py_file"],
            "level": "INFO",
            "propagate": False,
        }
    }
}

dictConfig(LOGGING_CONFIG)
