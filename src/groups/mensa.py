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

    @discord.ui.button(label='Mehr', style=discord.ButtonStyle.success)
    async def more_button(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        logger.info(f'{interaction.user} requested all lines ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})')
        no_mentions = discord.AllowedMentions.none()
        embed = self.plan.get_expanded_menu_embed(self.date)
        await interaction.response.send_message(content=f"<@{interaction.user.id}>", embed=embed, allowed_mentions=no_mentions)

    @discord.ui.button(label='Nährwerte & Umwelt-Score', style=discord.ButtonStyle.secondary)
    async def environment_button(self, interaction: discord.Interaction, button: discord.ui.Button):  # noqa
        logger.info(f'{interaction.user} requested the nutri-score menu ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})')
        await interaction.response.send_message(view=LineSelectMenu(self.plan, self.date, timeout=28800), ephemeral=True)


class LineSelectMenu(discord.ui.View):

    def __init__(self, plan: Plan, date: datetime.date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan
        self.date = date

        options = []
        for name in self.plan.list_lines_for_date(self.date):
            options.append(discord.SelectOption(label=name, value=name))

        # Fallback, wenn keine Linien vorhanden sind
        if not options:
            options = [discord.SelectOption(label='Keine Linien verfügbar', value='')]

        select = discord.ui.Select(placeholder='Wähle eine Linie', min_values=1, max_values=1, options=options)
        select.callback = self._on_select  # type: ignore[attr-defined]
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction):  # type: ignore[override]
        select: discord.ui.Select = interaction.data  # not used directly; discord passes selected via view children
        # safer: read from the children select
        selected_value = None
        for child in self.children:
            if isinstance(child, discord.ui.Select) and child.values:
                selected_value = child.values[0]
                break

        if not selected_value:
            await interaction.response.send_message('Keine Linie ausgewählt.', ephemeral=True)
            return

        logger.info(f'{interaction.user} requested the nutri score for line {selected_value} ({interaction.user.id} in {interaction.guild.id}.{interaction.channel.id})')
        environment_embed = self.plan.get_environment_embed(self.date, selected_value)
        nutri_embed = self.plan.get_nutri_embed(self.date, selected_value)
        await interaction.response.send_message(embeds=[e for e in (nutri_embed, environment_embed) if e], ephemeral=True)
