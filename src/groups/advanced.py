import logging
import os
import time
import discord
import git
from discord import app_commands
from src.plan import Plan

logger = logging.getLogger("bot")


class Advanced(app_commands.Group):

    def __init__(self, plan: Plan, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan

    @app_commands.command()
    async def version(self, interaction: discord.Interaction):
        logger.info(f"{interaction.user} requested the bot version - {interaction.data['options']} "
                    f"({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        sha = repo.head.object.hexsha
        await interaction.response.send_message(sha)  # noqa

    @app_commands.command()
    async def update(self, interaction: discord.Interaction):
        logger.info(f"{interaction.user} requested a plan update - {interaction.data['options']} "
                    f"({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        await interaction.response.defer(ephemeral=True, thinking=True)  # noqa
        await self.plan.update_plan()
        await interaction.followup.send(f"Speiseplan aktualisiert.", ephemeral=False)

    @app_commands.command()
    async def home(self, interaction: discord.Interaction):
        logger.info(f"{interaction.user} requested the source code - {interaction.data['options']} "
                    f"({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        await interaction.response.send_message("https://github.com/Hartmannlight/Mensa-am-Adenauerring")  # noqa

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        logger.info(f"{interaction.user} requested the ping - {interaction.data['options']} "
                    f"({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})")

        latency = interaction.created_at.timestamp() - time.time()
        await interaction.response.send_message(f"Pong! ({latency * 1000:.0f}ms)")  # noqa
