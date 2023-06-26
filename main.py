import config
import menu_grabber
from groups.advanced import Advanced
from groups.mensa import Mensa

import datetime
import holidays
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks


# todos:
# - add a docker-compose file for my image
# - stick with .env config?
# - configurable automatic daily post
# - edit / update automatic post
# - error handling
# - non-blocking update if possible
# - menu preview for the next days
# - command for koeri and cafeteria
# - show last update time
# - allergens to screenshot


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

    post_menu.start()
    update_menu.start()
    print("started tasks")


def post_today():
    today = datetime.date.today()

    # only on weekdays
    if today.weekday() >= 5:
        return False

    # not on public holidays
    public_holidays = holidays.country_holidays("DE", subdiv="BW")
    if public_holidays.get(today):
        return False

    return True


# 09:30 Berlin time
@tasks.loop(time=datetime.time(hour=9, minute=30, tzinfo=ZoneInfo("Europe/Berlin")))
async def post_menu():
    # tasks.loop only allows time objects, not datetime objects
    # so, we need to filter out if we want to post here
    if not post_today():
        print("Not posting menu today")
        return
    print("Time to post the menu for today")
    await bot.get_channel(config.CHANNEL_ID).send(embed=menu_grabber.get_menu_embed(datetime.date.today()))


@tasks.loop(seconds=config.UPDATE_INTERVAL)
async def update_menu():
    print("Auto update started")
    menu_grabber.update_menu(datetime.date.today())
    print("Auto update finished")


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
