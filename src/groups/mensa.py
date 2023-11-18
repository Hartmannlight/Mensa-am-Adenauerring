import datetime
import logging

import discord
from discord import app_commands

from src.plan import Plan

logger = logging.getLogger("bot")


class Mensa(app_commands.Group):

    def __init__(self, plan: Plan, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan

    @app_commands.command()
    async def embed(self, interaction: discord.Interaction, days_ahead: int = 0):

        date = datetime.date.today() + datetime.timedelta(days=days_ahead)

        logger.info(f"{interaction.user} requested the menu for {date} - {interaction.data['options']} "
                    f"({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        embed = self.plan.get_embed(date)
        if embed is None:
            await interaction.response.send_message(f'Kein Menü für {date.strftime("%A den %d.%m.%Y")} gefunden.', ephemeral=True)  # noqa
        else:
            await interaction.response.send_message(embed=embed)  # noqa

    @app_commands.command()
    async def screenshot(self, interaction: discord.Interaction, days_ahead: int = 0):
        logger.info(f"{interaction.user} requested a menu screenshot - {interaction.data['options']} "
                    f"({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        await interaction.response.send_message("Diese Funktion wurde aus technischen Gründen entfernt.", ephemeral=True)  # noqa
