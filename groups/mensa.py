import datetime
import discord
from discord import app_commands
import plan


class Mensa(app_commands.Group):

    @app_commands.command()
    async def embed(self, interaction: discord.Interaction, days_ahead: int = 0):

        date = datetime.date.today() + datetime.timedelta(days=days_ahead)
        print(f'{interaction.user} requested embedded menu for {date.strftime("%Y-%m-%d")}')

        try:
            embed = plan.get_embed(date)
            await interaction.response.send_message(embed=embed)  # noqa
        except KeyError:
            await interaction.response.send_message(f'Kein Menü für {date.strftime("%A %d.%m.%Y")} gefunden.', ephemeral=True)  # noqa

    @app_commands.command()
    async def screenshot(self, interaction: discord.Interaction, days_ahead: int = 0):
        print(f'{interaction.user} requested a screenshot')
        await interaction.response.send_message("Diese Funktion wurde aus technischen Gründen entfernt.", ephemeral=True)  # noqa
