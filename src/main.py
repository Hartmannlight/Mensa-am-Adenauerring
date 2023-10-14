
import config
from src import plan

import logging

import datetime
import holidays
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from groups.advanced import Advanced
from groups.mensa import Mensa


bot = discord.Client(intents=discord.Intents.default())
tree = discord.app_commands.CommandTree(bot)
logger = logging.getLogger("bot")


@bot.event
async def on_ready():
    logger.info(f"{bot.user} connected to Discord")
    tree.add_command(Mensa(name="mensa", description="Zeigt den aktuellen Speiseplan der Mensa an."))
    tree.add_command(Advanced(name="advanced", description="Entwickler-Optionen"))
    tree.copy_global_to(guild=discord.Object(id=config.GUILD))
    await tree.sync(guild=discord.Object(id=config.GUILD))
    logger.debug("Command tree has been synced")

    daily_post.start()
    update_plan.start()


@tasks.loop(time=datetime.time(hour=9, minute=30, tzinfo=ZoneInfo("Europe/Berlin")))
async def daily_post():
    logger.debug("Preparing daily post")
    today = datetime.date.today()
    public_holidays = holidays.country_holidays("DE", subdiv="BW")
    if today.weekday() >= 5 or public_holidays.get(today):
        logger.info(f"Skipping daily post on {today} because it's a public holiday or the weekend")
        return

    embed = plan.get_embed(today)
    await bot.get_channel(config.CHANNEL_ID).send(embed=embed)
    logger.info(f"Daily post on {today} has been sent")


@tasks.loop(seconds=config.UPDATE_INTERVAL)
async def update_plan():
    await plan.update_plan()


if __name__ == "__main__":
    bot.run(token=config.BOT_TOKEN, root_logger=True)
