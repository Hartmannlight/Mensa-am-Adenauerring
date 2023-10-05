
import discord
import datetime

import menu_grabber
from menu import Menu


async def update_plan():
    global plan
    delete_plan()

    curren_week = datetime.date.today().isocalendar()[1]
    plan = await menu_grabber.get_week_plan(curren_week)


def delete_plan():
    plan.clear()


def add_menu(date: datetime.date, menu: Menu):
    plan[date] = menu


def get_menu(date: datetime.date) -> Menu:
    if date not in plan:
        raise KeyError(f'No menu for {date} found')
    else:
        return plan[date]


def get_embed(date: datetime.date) -> discord.Embed:
    menu = get_menu(date)

    embed = discord.Embed(color=0xff2f00)

    title = f'Mensaeinheitsbrei der Mensa am Adenauerring - {date.strftime("%A %d.%m.%Y")}'
    link = f'https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/?kw={date.isocalendar()[1]}'

    embed.set_author(name=title, url=link)
    embed.set_footer(text="🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan")

    embed.add_field(name="Linie 1 Gut & Günstig", value=str(menu.lines[0]))
    embed.add_field(name="Linie 2 Vegane Linie", value=str(menu.lines[1]))
    embed.add_field(name="Linie 3", value=str(menu.lines[2]))
    embed.add_field(name="Linie 4", value=str(menu.lines[3]))
    embed.add_field(name="Linie 5", value=str(menu.lines[4]))
    embed.add_field(name="Linie 6", value=str(menu.lines[6]))
    embed.add_field(name="[pizza]werk", value=str(menu.lines[12]) + "\n" + str(menu.lines[10]))
    return embed


plan = {}
