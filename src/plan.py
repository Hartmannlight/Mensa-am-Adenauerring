import asyncio
import datetime
import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import discord  # noqa

import fetcher

logger = logging.getLogger('bot')


def _nwsp() -> str:
    return '​'  # zero-width no-break space


def _norm_key(name: str) -> str:
    return re.sub(r'\s+', ' ', name.strip().lower())


def _looks_like(name: str, *patterns: str) -> bool:
    key = _norm_key(name)
    return any(p in key for p in patterns)


class Plan:
    def __init__(self) -> None:
        self.menus: Dict[datetime.date, Dict[str, List[Dict[str, Any]]]] = {}
        self.last_update = datetime.datetime(1970, 1, 1)
        self._source_url = 'https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/'

    async def update_plan(self) -> None:
        try:
            out = await fetcher.extract_async([self._source_url], day_label=None)
        except Exception as e:
            logger.error('Error while updating plan: %s', e)
            return

        grouped: Dict[datetime.date, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
        for m in out.get('meals', []):
            try:
                d = datetime.date.fromisoformat(m.get('day_iso') or '')
            except Exception:
                continue
            line = m.get('line') or 'Unbekannte Linie'
            grouped[d][line].append(m)

        self.menus = {d: dict(lines) for d, lines in grouped.items()}
        self.last_update = datetime.datetime.now()
        logger.info('Plan updated: days=%d', len(self.menus))

    def _format_line(self, meals: List[Dict[str, Any]]) -> str:
        rows: List[str] = []
        for m in meals:
            emoji = m.get('diet_emoji') or ''
            title = m.get('title') or ''
            price = m.get('prices', {}).get('students')
            price_s = f'{price:.2f} €' if isinstance(price, (int, float)) else ''
            rows.append(f'{emoji}{title} — {price_s}'.rstrip(' —'))
        return '\n'.join(rows) if rows else '—'

    def _pick_line(self, lines: Dict[str, List[Dict[str, Any]]], *predicates: Tuple[str, ...]) -> Tuple[str, List[Dict[str, Any]]]:
        for name, meals in lines.items():
            if _looks_like(name, *predicates):
                return name, meals
        return '', []

    def get_embed_template(self, date: datetime.date) -> discord.Embed:
        embed = discord.Embed(color=0xff2f00)
        title = f'Mensaeinheitsbrei der Mensa am Adenauerring - {date.strftime("%A %d.%m.%Y")}'
        link = f'https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/?kw={date.isocalendar()[1]}'
        embed.set_author(name=title, url=link)
        embed.set_footer(
            text='🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan'
                 '                                           '
                 f'Stand: {self.last_update.strftime("%d.%m  %H:%M Uhr")}'
        )
        return embed

    def get_menu_embed(self, date: datetime.date) -> discord.Embed | None:
        lines = self.menus.get(date)
        if not lines:
            logger.info('No menu for %s found', date)
            return None

        embed = self.get_embed_template(date)

        def add_pair(a_patterns: Tuple[str, ...], b_patterns: Tuple[str, ...], a_fallback: str, b_fallback: str) -> None:
            name_a, meals_a = self._pick_line(lines, *a_patterns)
            name_b, meals_b = self._pick_line(lines, *b_patterns)
            if meals_a:
                embed.add_field(name=name_a or a_fallback, value=self._format_line(meals_a) + '\n')
            if meals_b:
                embed.add_field(name=name_b or b_fallback, value=self._format_line(meals_b) + '\n')
            embed.add_field(name=_nwsp(), value=_nwsp())

        add_pair(('linie 1', 'gut & günstig', 'gut und günstig'), ('linie 2', 'vegane'), 'Linie 1', 'Linie 2')
        add_pair(('linie 3',), ('linie 4',), 'Linie 3', 'Linie 4')
        add_pair(('linie 5',), ('linie 6',), 'Linie 5', 'Linie 6')

        pizza_name, pizza_meals = self._pick_line(lines, 'pizza')
        koeri_name, koeri_meals = self._pick_line(lines, 'kœri', 'kori', 'köri', 'koeri', 'koeriwerk')
        text = ''
        if pizza_meals:
            text += self._format_line(pizza_meals)
        if koeri_meals:
            if text:
                text += '\n'
            text += self._format_line(koeri_meals)
        if text:
            embed.add_field(name=pizza_name or '[pizza]werk', value=text, inline=False)

        return embed

    def get_expanded_menu_embed(self, date: datetime.date) -> discord.Embed:
        lines = self.menus.get(date) or {}
        embed = self.get_embed_template(date)

        def add_if(name_like: Tuple[str, ...], title_fallback: str, inline: bool) -> None:
            name, meals = self._pick_line(lines, *name_like)
            if meals:
                embed.add_field(name=name or title_fallback, value=self._format_line(meals) + '\n', inline=inline)

        add_if(('kœri', 'kori', 'köri', 'koeri', 'koeriwerk'), '[KŒRI]WERK', False)
        add_if(('schnitzel',), 'Schnitzelbar', False)
        add_if(('cafeteria',), 'Cafeteria', True)
        add_if(('spätausgabe', 'spae', 'spat'), 'Spätausgabe', True)

        return embed

    def _get_line_meals_by_label(self, date: datetime.date, line_label: str) -> List[Dict[str, Any]]:
        lines = self.menus.get(date) or {}
        for name, meals in lines.items():
            if _norm_key(name) == _norm_key(line_label):
                return meals
        return []

    def get_environment_embed(self, date: datetime.date, line_label: str) -> discord.Embed | None:
        meals = self._get_line_meals_by_label(date, line_label)
        embed = discord.Embed(color=0xff2f00)
        embed.set_author(name='Umwelt-Score')
        for m in meals:
            imp = m.get('impact') or {}
            if not any([imp.get('co2_g'), imp.get('water_l'), imp.get('animal_welfare_rating'), imp.get('rainforest_rating')]):
                continue
            lines: List[str] = []
            if imp.get('co2_g') is not None:
                lines.append(f'CO₂: {imp["co2_g"]:.0f} g')
            if imp.get('water_l') is not None:
                lines.append(f'Wasser: {imp["water_l"]:.1f} l')
            if imp.get('animal_welfare_rating') is not None:
                lines.append(f'Tierwohl: {imp["animal_welfare_rating"]}/5')
            if imp.get('rainforest_rating') is not None:
                lines.append(f'Regenwald: {imp["rainforest_rating"]}/5')
            if lines:
                embed.add_field(name=m.get('title') or 'Gericht', value='\n'.join(lines) + '\n', inline=False)
        return embed

    def get_nutri_embed(self, date: datetime.date, line_label: str) -> discord.Embed | None:
        meals = self._get_line_meals_by_label(date, line_label)
        embed = discord.Embed(color=0xff2f00)
        embed.set_author(name='Nährwerte')
        for m in meals:
            n = m.get('nutrition') or {}
            if not any([n.get('energy_kj'), n.get('energy_kcal'), n.get('protein_g'), n.get('carbs_g'),
                        n.get('sugar_g'), n.get('fat_g'), n.get('sat_fat_g'), n.get('salt_g')]):
                continue
            rows: List[str] = []
            if n.get('energy_kj') is not None and n.get('energy_kcal') is not None:
                rows.append(f'Energie: {n["energy_kj"]:.0f} kJ / {n["energy_kcal"]:.0f} kcal')
            if n.get('protein_g') is not None:
                rows.append(f'Protein: {n["protein_g"]:.1f} g')
            if n.get('carbs_g') is not None:
                rows.append(f'Carbs: {n["carbs_g"]:.1f} g')
            if n.get('sugar_g') is not None:
                rows.append(f'Zucker: {n["sugar_g"]:.1f} g')
            if n.get('fat_g') is not None:
                rows.append(f'Fett: {n["fat_g"]:.1f} g')
            if n.get('sat_fat_g') is not None:
                rows.append(f'ges. Fett: {n["sat_fat_g"]:.1f} g')
            if n.get('salt_g') is not None:
                rows.append(f'Salz: {n["salt_g"]:.2f} g')
            if rows:
                embed.add_field(name=m.get('title') or 'Gericht', value='\n'.join(rows) + '\n', inline=False)
        return embed

    def list_lines_for_date(self, date: datetime.date) -> List[str]:
        lines = self.menus.get(date) or {}
        return sorted(lines.keys(), key=lambda s: _norm_key(s))
