import datetime
import logging

import discord  # noqa
from discord import app_commands  # noqa

from src.plan import Plan

logger = logging.getLogger("bot")


class Mensa(app_commands.Group):

    def __init__(self, plan: Plan, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan

    @app_commands.command()
    async def embed(self, interaction: discord.Interaction, days_ahead: int = 0):
        date = datetime.date.today() + datetime.timedelta(days=days_ahead)
        logger.info(f"{interaction.user} requested the menu for {date} - {interaction.data['options']} ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        embed = self.plan.get_menu_embed(date)
        if embed is None:
            await interaction.response.send_message(f'Kein Menü für {date.strftime("%A den %d.%m.%Y")} gefunden.', ephemeral=True)  # noqa
        else:
            await interaction.response.send_message(embed=embed, view=Buttons(self.plan, days_ahead, timeout=28800))  # noqa


class Buttons(discord.ui.View):

    def __init__(self, plan: Plan, days_ahead: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan
        self.date = datetime.date.today() + datetime.timedelta(days=days_ahead)

    @discord.ui.button(label="Mehr", style=discord.ButtonStyle.success)
    async def more_button(self, interaction, button):
        logger.info(f"{interaction.user} requested all lines ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        embed = self.plan.get_expanded_menu_embed(self.date)
        await interaction.response.send_message(embed=embed)  # noqa

    @discord.ui.button(label="Nährwerte & Umwelt-Score", style=discord.ButtonStyle.secondary)
    async def environment_button(self, interaction, button):
        logger.info(f"{interaction.user} requested the nutri-score menu ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")
        await interaction.response.send_message(view=LineSelectMenu(self.plan, self.date, timeout=28800), ephemeral=True)


class LineSelectMenu(discord.ui.View):

    def __init__(self, plan: Plan, date: datetime.date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan
        self.date = date

    @discord.ui.select(
        placeholder="Wähle ein Linie",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Linie 1",
                description="Gut & Günstig",
                value="0"
            ),
            discord.SelectOption(
                label="Linie 2",
                description="Vegane Linie",
                value="1"
            ),
            discord.SelectOption(
                label="Linie 3",
                description="",
                value="2"
            ),
            discord.SelectOption(
                label="Linie 4",
                description="",
                value="3"
            ),
            discord.SelectOption(
                label="Linie 5",
                description="",
                value="4"
            ),
            discord.SelectOption(
                label="Linie 6",
                description="",
                value="6"
            ),
            discord.SelectOption(
                label="[pizza]werk",
                description="",
                value="10"
            ),
            discord.SelectOption(
                label="[KŒRI]WERK",
                description="Die einzig wahre Linie",
                value="8"
            ),

        ]
    )
    async def select_callback(self, interaction, select):
        logger.info(f"{interaction.user} requested the nutri score for line {select.values[0]} ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")
        environment_embed = self.plan.get_environment_embed(self.date, int(select.values[0]))
        nutri_embed = self.plan.get_nutri_embed(self.date, int(select.values[0]))
        await interaction.response.send_message(embeds=[nutri_embed, environment_embed], ephemeral=True)
