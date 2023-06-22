import config
import MenuGrabber

import datetime
import holidays
from zoneinfo import ZoneInfo

from io import BytesIO

import discord
from discord.ext import commands, tasks
from discord import app_commands


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

menu = MenuGrabber.Menu()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=[], intents=discord.Intents.default())

    async def setup_hook(self):
        print("Setting up...")
        await self.tree.sync(guild=discord.Object(id=config.GUILD))
        menu.update()
        print("Setup complete.")

    async def on_ready(self):
        post_menu.start()
        update_menu.start()


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
    print("Posting menu")
    await bot.get_channel(config.CHANNEL_ID).send(embed=get_menu_embed())


@tasks.loop(seconds=config.UPDATE_INTERVAL)
async def update_menu():
    print("Updating menu")
    menu.update()


def get_menu_embed():
    embed = discord.Embed(title="Mensaeinheitsbrei der Mensa am Adenauerring - " + datetime.date.today().strftime("%A %d.%m.%Y"), color=0xff2f00)
    embed.set_footer(text="🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan")

    embed.add_field(name="Linie 1 Gut & Günstig", value="\n".join(menu.text[0]))
    embed.add_field(name="Linie 2 Vegane Linie", value="\n".join(menu.text[1]))
    embed.add_field(name="Linie 3", value="\n".join(menu.text[2]))
    embed.add_field(name="Linie 4", value="\n".join(menu.text[3]))
    embed.add_field(name="Linie 5", value="\n".join(menu.text[4]))
    embed.add_field(name="Linie 6", value="\n".join(menu.text[6]))
    embed.add_field(name="[pizza]werk", value="\n".join(menu.text[12]) + "\n" + "\n".join(menu.text[10]))
    return embed


bot = Bot()


@bot.hybrid_command(name="update", description="Aktualisiert den Speiseplan.")
@app_commands.guilds(discord.Object(id=config.GUILD))
async def mensa(ctx: commands.Context):
    print(f"Updating menu, author: {ctx.author}")
    await ctx.reply("Aktualisiere Speiseplan...")
    menu.update()
    await ctx.reply("Speiseplan aktualisiert.")


@bot.hybrid_command(name="mensa", description="Gibt den heutigen Speiseplan der Mensa am Adenauerring aus.")
@app_commands.guilds(discord.Object(id=config.GUILD))
async def mensa(ctx: commands.Context, response_format: str = "embed"):
    if response_format == "embed":
        await mensa_embed(ctx)
    elif response_format == "screenshot" or response_format == "image" or response_format == "bild":
        await mensa_screenshot(ctx)
    else:
        await ctx.reply("Bitte gib ein gültiges Format an: `embed`, `screenshot`")


async def mensa_embed(ctx: commands.Context):
    await ctx.reply(embed=get_menu_embed())


async def mensa_screenshot(ctx: commands.Context):
    await ctx.reply(file=discord.File(BytesIO(menu.screenshot), filename=datetime.date.today().strftime('%Y-%m-%d.png')))


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
