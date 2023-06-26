import datetime
import time

import git
import discord
from discord import app_commands

import menu_grabber


class Advanced(app_commands.Group):
    @app_commands.command()
    async def version(self, interaction: discord.Interaction):
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        await interaction.response.send_message(sha)

    @app_commands.command()
    async def update(self, interaction: discord.Interaction):
        print(f'{interaction.user} requested an update')
        await interaction.response.defer(ephemeral=True, thinking=True)
        menu_grabber.update_menu(datetime.date.today())
        await interaction.followup.send(f"Speiseplan aktualisiert.", ephemeral=False)

    @app_commands.command()
    async def home(self, interaction: discord.Interaction):
        await interaction.response.send_message("https://github.com/Hartmannlight/Mensa-am-Adenauerring")

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        latency = interaction.created_at.timestamp() - time.time()
        await interaction.response.send_message(f"Pong! ({latency * 1000:.0f}ms)")
