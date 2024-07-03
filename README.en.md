[Deutsch](README.md) | [English](README.en.md)

# Discord Mensa Bot
A Discord bot that provides information about the menu at the "Mensa am Adenauerring" of the Karlsruhe Institute of Technology (KIT). Each day, the current menu is posted in the form of an embed in a selected channel and updated throughout the day.

## Commands

### `/mensa embed days_ahead: x`
Displays the cafeteria offerings x days in advance. `days_ahead` is optional.

### `/advanced home`
Posts a link to the bot's source code.

### `/advanced ping`
The application responds with the time (in milliseconds) it took to receive the command.

### `/advanced update`
Manually triggers an update of the menu.

### `/advanced version`
Outputs the current Git hash of the commit the application is running on.

## Setup

The project offers a ready-to-use Docker image as a package. In the `docker-compose.yaml` there is a sample configuration. This configuration needs to be supplemented and saved with the following information:

### Required Environment Variables:
- `BOT_TOKEN`: This can be created in the [Discord Developer Portal](https://discord.com/developers/applications?new_application=true).
- `GUILD`: The server ID where the bot should run.
- `CHANNEL_ID`: The channel where the cafeteria offerings will be posted on weekdays.

### Optional Environment Variables:
- `UPDATE_INTERVAL`: Time interval in seconds after which the menu is fetched from the cafeteria website and updated in the Discord embed if there are changes (default: 3600 seconds).

Then the application can be started with the command `docker compose up -d`. You can find instructions for installing Docker Compose online.

## Development

Would you like to contribute to the project? You can clone the project from GitHub and run it in a virtual environment (venv). Write the aforementioned environment variables in a `.env` file and place it in the directory.

You can install the dependencies with `pip install -r ./requirements.txt`.

## Additional Notes:
- The bot currently posts the menu at 9:30 AM.
- The bot can be used in an announcement channel and will then also publish the menu to servers that have subscribed to this channel.
- Please consider subscribing to the announcement channel of the KIT Math-Info server and, if not otherwise possible, do not set the update interval of your instance too high to keep the traffic on www.sw-ka.de low.
- The bot creates logs to prevent misuse.
- The bot only supports modern slash commands.
