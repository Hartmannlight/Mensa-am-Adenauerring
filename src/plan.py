import datetime
import logging

import discord
from discord import Embed

import menu_grabber

logger = logging.getLogger("bot")


class Plan:

    def __init__(self):
        self.menus = {}

    async def update_plan(self):
        curren_week = datetime.date.today().isocalendar()[1]

        try:
            self.menus = await menu_grabber.get_week_plan(curren_week)
        except Exception as e:
            logger.error(f'Error while updating plan: {e}')
            raise e

    def get_embed(self, date: datetime.date) -> Embed | None:
        menu = self.menus.get(date)
        if menu is None:
            logger.info(f'No menu for {date} found')
            return None

        embed = discord.Embed(color=0xff2f00)

        title = f'Mensaeinheitsbrei der Mensa am Adenauerring - {date.strftime("%A %d.%m.%Y")}'
        link = f'https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/?kw={date.isocalendar()[1]}'

        embed.set_author(name=title, url=link)
        embed.set_footer(text="🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan" +
                              "                                           " +  # S P A C E S
                              f"Stand: {datetime.datetime.now().strftime('%d.%m  %H:%M Uhr')}")

        embed.add_field(name="Linie 1 Gut & Günstig", value=str(menu.lines[0]))
        embed.add_field(name="Linie 2 Vegane Linie", value=str(menu.lines[1]))
        embed.add_field(name="Linie 3", value=str(menu.lines[2]))
        embed.add_field(name="Linie 4", value=str(menu.lines[3]))
        embed.add_field(name="Linie 5", value=str(menu.lines[4]))
        embed.add_field(name="Linie 6", value=str(menu.lines[6]))
        embed.add_field(name="[pizza]werk", value=str(menu.lines[12]) + "\n" + str(menu.lines[10]))
        return embed
