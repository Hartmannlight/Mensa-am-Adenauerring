import config
import MenuGrabber
import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
from io import BytesIO


# todos:
# - add error handling
# - add menu preview for the next days
# - add command for koeri and cafeteria
# - show last update time
# - clean up docker files
# - add allergens to screenshot

menu = MenuGrabber.Menu()


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("Setting up...")
        await self.tree.sync(guild=discord.Object(id=config.GUILD))
        menu.update()
        print("Setup complete.")


bot = Bot()


# update menu every day at 00:05
@tasks.loop(time=datetime.time(hour=22, minute=5))  # utc time
async def update_menu():
    print("Automatically updating menu")
    menu.update()


# update menu with discord command
@bot.hybrid_command(name="update", description="Aktualisiert den Speiseplan.")
@app_commands.guilds(discord.Object(id=config.GUILD))
async def mensa(ctx: commands.Context):
    await ctx.reply("Aktualisiere Speiseplan...")
    menu.update()
    await ctx.reply("Speiseplan aktualisiert.")


# access menu with discord command
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
    embed = discord.Embed(title="Mensaeinheitsbrei der Mensa-am-Adenauerring - " + datetime.date.today().strftime('%A %d.%m.%Y'), color=0xff2f00)
    embed.set_footer(text="🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan")

    embed.add_field(name="Linie 1 Gut & Günstig", value="\n".join(menu.text[0]))
    embed.add_field(name="Linie 2 Vegane Linie", value="\n".join(menu.text[1]))
    embed.add_field(name="Linie 3", value="\n".join(menu.text[2]))
    embed.add_field(name="Linie 4", value="\n".join(menu.text[3]))
    embed.add_field(name="Linie 5", value="\n".join(menu.text[4]))
    embed.add_field(name="Linie 6", value="\n".join(menu.text[6]))
    embed.add_field(name="[PIZZA]WERK", value="\n".join(menu.text[12]) + "\n" + "\n".join(menu.text[10]))

    await ctx.reply(embed=embed)


async def mensa_screenshot(ctx: commands.Context):
    await ctx.reply(file=discord.File(BytesIO(menu.screenshot), filename=datetime.date.today().strftime('%Y-%m-%d.png')))

bot.run(config.BOT_TOKEN)
