
import config
import plan

import datetime
import holidays
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from groups.advanced import Advanced
from groups.mensa import Mensa


bot = discord.Client(intents=discord.Intents.default())
tree = discord.app_commands.CommandTree(bot)


@bot.event
async def on_ready():

    print("Logged in as", bot.user.name, bot.user.id)

    tree.add_command(Mensa(name="mensa", description="Zeigt den aktuellen Speiseplan der Mensa an."))
    tree.add_command(Advanced(name="advanced", description="Entwickler-Optionen"))
    tree.copy_global_to(guild=discord.Object(id=config.GUILD))
    await tree.sync(guild=discord.Object(id=config.GUILD))
    print("synced commands")

    daily_post.start()
    update_plan.start()
    print("started tasks")


@tasks.loop(time=datetime.time(hour=9, minute=30, tzinfo=ZoneInfo("Europe/Berlin")))
async def daily_post():
    print("Daily post started")
    today = datetime.date.today()
    public_holidays = holidays.country_holidays("DE", subdiv="BW")
    if today.weekday() >= 5 or public_holidays.get(today):
        return

    embed = plan.get_embed(today)
    await bot.get_channel(config.CHANNEL_ID).send(embed=embed)
    print("Daily post finished")


@tasks.loop(seconds=config.UPDATE_INTERVAL)
async def update_plan():
    print("Auto update started")
    await plan.update_plan()
    print("Auto update finished")


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
