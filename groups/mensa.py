import datetime
from io import BytesIO

import discord
from discord import app_commands

import menu_grabber


class Mensa(app_commands.Group):
    @app_commands.command()
    async def embed(self, interaction: discord.Interaction, days_ahead: int = 0):

        date = datetime.date.today() + datetime.timedelta(days=days_ahead)
        print(f'{interaction.user} requested embedded menu for {date.strftime("%Y-%m-%d")}')

        try:
            embed = menu_grabber.get_menu_embed(date)
        except ValueError:
            await interaction.response.send_message("Kein Menü für dieses Datum gefunden", ephemeral=True)
            print(f'No menu found for {date.strftime("%Y-%m-%d")}')
            return

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    async def screenshot(self, interaction: discord.Interaction, days_ahead: int = 0):
        date = datetime.date.today() + datetime.timedelta(days=days_ahead)
        print(f'{interaction.user} requested a screenshot for {date.strftime("%Y-%m-%d")}')

        try:
            screenshot = menu_grabber.get_menu(date).screenshot
        except ValueError:
            await interaction.response.send_message("Kein Menü für dieses Datum gefunden", ephemeral=True)
            print(f'No menu found for {date.strftime("%Y-%m-%d")}')
            return

        await interaction.response.send_message(file=discord.File(BytesIO(screenshot), filename=date.strftime('%Y-%m-%d.png')))
