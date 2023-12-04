import datetime
import logging

import discord  # noqa
from discord import Embed  # noqa

import menu_grabber

logger = logging.getLogger("bot")


class Plan:

    def __init__(self):
        self.menus = {}
        self.last_update = datetime.datetime(1970, 1, 1)

    async def update_plan(self):
        curren_week = datetime.date.today().isocalendar()[1]

        try:
            self.menus = await menu_grabber.get_week_plan(curren_week)
            self.last_update = datetime.datetime.now()
        except Exception as e:
            logger.error(f'Error while updating plan: {e}')

    def get_menu_embed(self, date: datetime.date) -> Embed | None:
        menu = self.menus.get(date)
        if menu is None:
            logger.info(f'No menu for {date} found')
            return None

        embed = self.get_embed_template(date)
        embed.add_field(name="Linie 1 Gut & Günstig", value=str(menu.lines[0]) + "\n")
        embed.add_field(name="Linie 2 Vegane Linie", value=str(menu.lines[1]) + "\n")
        embed.add_field(name="​", value="​")

        embed.add_field(name="Linie 3", value=str(menu.lines[2]) + "\n")
        embed.add_field(name="Linie 4", value=str(menu.lines[3]) + "\n")
        embed.add_field(name="​", value="​")

        embed.add_field(name="Linie 5", value=str(menu.lines[4]) + "\n")
        embed.add_field(name="Linie 6", value=str(menu.lines[6]) + "\n")
        embed.add_field(name="​", value="​")

        embed.add_field(name="[pizza]werk", value=str(menu.lines[12]) + "\n" + str(menu.lines[10]), inline=False)
        return embed

    def get_expanded_menu_embed(self, date: datetime.date) -> Embed:
        menu = self.menus.get(date)
        embed = self.get_embed_template(date)

        if menu is None:
            return embed

        embed.add_field(name="[KŒRI]WERK", value=str(menu.lines[8]) + "\n", inline=False)
        embed.add_field(name="Schnitzelbar", value=str(menu.lines[5]) + "\n", inline=False)
        embed.add_field(name="Cafeteria", value=str(menu.lines[9]) + "\n", inline=True)
        embed.add_field(name="Spätausgabe", value=str(menu.lines[7]) + "\n", inline=True)

        return embed

    def get_embed_template(self, date: datetime.date) -> Embed | None:

        embed = discord.Embed(color=0xff2f00)
        title = f'Mensaeinheitsbrei der Mensa am Adenauerring - {date.strftime("%A %d.%m.%Y")}'
        link = f'https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/?kw={date.isocalendar()[1]}'
        embed.set_author(name=title, url=link)
        embed.set_footer(text="🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan" +
                              "                                           " +  # S P A C E S
                              f"Stand: {self.last_update.strftime('%d.%m  %H:%M Uhr')}")
        return embed

    def get_environment_embed(self, date: datetime.date, line: int) -> Embed | None:
        menu = self.menus.get(date)
        line = menu.lines[line]

        embed = discord.Embed(color=0xff2f00)
        embed.set_author(name="Umwelt-Score")

        for meal in line.meals:
            if meal.environmental_score is None:
                continue
            embed.add_field(name=meal.name, value=str(meal.environmental_score) + "\n", inline=False)

        return embed

    def get_nutri_embed(self, date: datetime.date, line: int) -> Embed | None:
        menu = self.menus.get(date)
        line = menu.lines[line]

        embed = discord.Embed(color=0xff2f00)
        embed.set_author(name="Nährwerte")

        for meal in line.meals:
            if meal.nutri_score is None:
                continue
            embed.add_field(name=meal.name, value=str(meal.nutri_score) + "\n", inline=False)

        return embed
