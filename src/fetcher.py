from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

import httpx
from bs4 import BeautifulSoup, Tag

log = logging.getLogger('bot.fetcher')


class Diet:
    def __init__(self, abbreviation: str | None):
        if abbreviation == 'mt-0':
            self.emoji = ''
        elif abbreviation == 'mt-1':
            self.emoji = '🍖 '
        elif abbreviation == 'mt-2':
            self.emoji = '🍖 '
        elif abbreviation == 'mt-3':
            self.emoji = '🐟 '
        elif abbreviation == 'mt-4':
            self.emoji = ''
        elif abbreviation == 'mt-5':
            self.emoji = ''
        elif abbreviation == 'mt-6':
            self.emoji = '🌻 '
        elif abbreviation == 'mt-7':
            self.emoji = '🌱 '
        elif abbreviation == 'mt-8':
            self.emoji = ''
        elif abbreviation == 'mt-9':
            self.emoji = ''
        else:
            self.emoji = ''


DIET_LABELS: dict[str, str] = {
    'mt-0': 'unknown',
    'mt-1': 'pork',
    'mt-2': 'beef',
    'mt-3': 'fish',
    'mt-4': 'unknown',
    'mt-5': 'unknown',
    'mt-6': 'vegan',
    'mt-7': 'vegetarian',
    'mt-8': 'unknown',
    'mt-9': 'unknown',
}


@dataclass
class Nutrition:
    energy_kj: float | None
    energy_kcal: float | None
    protein_g: float | None
    carbs_g: float | None
    sugar_g: float | None
    fat_g: float | None
    sat_fat_g: float | None
    salt_g: float | None
    units: dict[str, str]


@dataclass
class Impact:
    co2_g: float | None
    water_l: float | None
    animal_welfare_rating: int | None
    rainforest_rating: int | None


@dataclass
class Meal:
    line: str
    title: str
    allergens: list[str]
    prices: dict[str, float]
    nutrition: Nutrition | None
    impact: Impact | None
    day_iso: str
    day_label: str
    diet_abbreviation: str | None
    diet_label: str | None
    diet_emoji: str


PRICE_MAP = {
    'price_1': 'students',
    'price_2': 'guests',
    'price_3': 'staff',
    'price_4': 'pupils',
}


def _to_float(s: str | None) -> float | None:
    if not s:
        return None
    s = s.replace('\xa0', ' ').replace('.', '').replace(',', '.')
    m = re.search(r'(-?\d+(?:\.\d+)?)', s)
    return float(m.group(1)) if m else None


def _text(el: Tag | None) -> str:
    return el.get_text(strip=True) if el else ''


def _norm_rel(v: Any) -> str:
    if isinstance(v, list):
        return v[0] if v else ''
    return v or ''


def _find_info_cell(meal_tr: Tag) -> Tag | None:
    sib = meal_tr.find_next_sibling('tr')
    hops = 0
    while sib:
        td = sib.find('td', class_=lambda c: c and 'nutrition_facts_row' in c)
        if td:
            return td
        clist = sib.get('class') or []
        if any(c.startswith('mt-') for c in clist):
            log.debug('Reached next meal row while scanning info cell', extra={'skipped_rows': hops})
            return None
        sib = sib.find_next_sibling('tr')
        hops += 1
    return None


def _sel_one_text(root: Tag, css: str) -> str:
    el = root.select_one(css)
    return el.get_text(strip=True) if el else ''


def _detect_diet(meal_tr: Tag) -> tuple[str | None, str | None, str]:
    clist = meal_tr.get('class') or []
    abbr = next((c for c in clist if c.startswith('mt-')), None)
    label = DIET_LABELS.get(abbr, None) if abbr else None
    emoji = Diet(abbr).emoji if abbr else ''
    return abbr, label, emoji


def parse_menu(html: str) -> list[Meal]:
    t0 = time.perf_counter()
    soup = BeautifulSoup(html, 'lxml')

    day_nav = soup.select('ul.canteen-day-nav li a')
    day_index_to_meta = {
        i: {'iso': _norm_rel(a.get('rel')), 'label': _text(a)}
        for i, a in enumerate(day_nav, start=1)
    }

    day_divs = soup.select('div.canteen-day')
    log.debug('Parsing menu DOM', extra={'day_links': len(day_nav), 'day_blocks': len(day_divs)})

    meals: list[Meal] = []
    for day_div in day_divs:
        m = re.search(r'canteen_day_(\d+)', day_div.get('id', ''))
        if not m:
            log.debug('Day without index id found, skipped')
            continue
        idx = int(m.group(1))
        day_iso = day_index_to_meta.get(idx, {}).get('iso', '')
        day_label = day_index_to_meta.get(idx, {}).get('label', '')

        rows = day_div.select('tr.mensatype_rows')
        log.debug('Day block found', extra={'index': idx, 'label': day_label, 'iso': day_iso, 'rows': len(rows)})

        for row in rows:
            line_name = _text(row.select_one('td.mensatype div')).replace('\n', ' ').strip()
            inner = row.select_one('td.mensadata table.meal-detail-table')
            if not inner:
                log.debug('Row without inner meal table', extra={'line': line_name})
                continue

            for meal_tr in inner.select('tr[class^=mt-]'):
                title_cell = meal_tr.select_one('td.first.menu-title')
                if not title_cell:
                    log.debug('Meal without title cell', extra={'line': line_name})
                    continue

                title = _text(title_cell.select_one('span b'))
                allergens_raw = _text(title_cell.select_one('sup'))
                allergens: list[str] = []
                if allergens_raw.startswith('[') and allergens_raw.endswith(']'):
                    allergens = [a.strip() for a in allergens_raw.strip('[]').split(',') if a.strip()]

                prices: dict[str, float] = {}
                for span in meal_tr.select('span.bgp'):
                    for cls in span.get('class', []):
                        if cls in PRICE_MAP:
                            prices[PRICE_MAP[cls]] = _to_float(_text(span)) or 0.0

                diet_abbr, diet_label, diet_emoji = _detect_diet(meal_tr)

                nutrition: Nutrition | None = None
                impact: Impact | None = None
                info_td = _find_info_cell(meal_tr)
                if info_td:
                    nf = info_td.select_one('div.nutrition_facts')
                    if nf:
                        energy = _sel_one_text(nf, '.energie .value, .energie div:nth-of-type(2)')
                        kj = kcal = None
                        if energy:
                            em = re.search(r'([0-9.,]+)\s*kJ\s*/\s*([0-9.,]+)\s*kcal', energy.replace('\xa0', ' '))
                            if em:
                                kj = _to_float(em.group(1))
                                kcal = _to_float(em.group(2))

                        nutrition = Nutrition(
                            energy_kj=kj,
                            energy_kcal=kcal,
                            protein_g=_to_float(_sel_one_text(nf, '.proteine .value, .proteine div:nth-of-type(2)')),
                            carbs_g=_to_float(_sel_one_text(nf, '.kohlenhydrate .value, .kohlenhydrate div:nth-of-type(2)')),
                            sugar_g=_to_float(_sel_one_text(nf, '.zucker .value, .zucker div:nth-of-type(2)')),
                            fat_g=_to_float(_sel_one_text(nf, '.fett .value, .fett div:nth-of-type(2)')),
                            sat_fat_g=_to_float(_sel_one_text(nf, '.gesaettigt .value, .gesaettigt div:nth-of-type(2)')),
                            salt_g=_to_float(_sel_one_text(nf, '.salz .value, .salz div:nth-of-type(2)')),
                            units={
                                'energy_kj': 'kJ',
                                'energy_kcal': 'kcal',
                                'protein_g': 'g',
                                'carbs_g': 'g',
                                'sugar_g': 'g',
                                'fat_g': 'g',
                                'sat_fat_g': 'g',
                                'salt_g': 'g',
                                'basis': 'per portion',
                            },
                        )

                    co2_val = _to_float(_sel_one_text(info_td, '.co2_footprint .value, .co2_bewertung .value, .co2_bewertung_wolke .value'))
                    water_val = _to_float(_sel_one_text(info_td, '.wasser_bewertung .value, .wasser .value'))
                    aw = info_td.select_one('.tierwohl .enviroment_score, .tierwohl .environment_score')
                    rf = info_td.select_one('.regenwald .enviroment_score, .regenwald .environment_score')

                    def _rating(tag: Tag | None) -> int | None:
                        if not tag:
                            return None
                        val = tag.get('data-rating') or tag.get('data-score')
                        return int(val) if val else None

                    impact = Impact(
                        co2_g=co2_val,
                        water_l=water_val,
                        animal_welfare_rating=_rating(aw),
                        rainforest_rating=_rating(rf),
                    )

                meals.append(Meal(
                    line=line_name,
                    title=title,
                    allergens=allergens,
                    prices=prices,
                    nutrition=nutrition,
                    impact=impact,
                    day_iso=day_iso,
                    day_label=day_label,
                    diet_abbreviation=diet_abbr,
                    diet_label=diet_label,
                    diet_emoji=diet_emoji,
                ))

    label_counts: dict[str, int] = {}
    iso_counts: dict[str, int] = {}
    for m in meals:
        label_counts[m.day_label] = label_counts.get(m.day_label, 0) + 1
        iso_counts[m.day_iso] = iso_counts.get(m.day_iso, 0) + 1

    log.debug(
        'Menu parsed',
        extra={
            'meals': len(meals),
            'duration_s': round(time.perf_counter() - t0, 3),
            'day_labels': {k: v for k, v in sorted(label_counts.items())},
            'day_iso_values': {k: v for k, v in sorted(iso_counts.items())},
        },
    )
    return meals


async def _fetch_one(client: httpx.AsyncClient, source: str) -> tuple[str, str]:
    t0 = time.perf_counter()
    try:
        if source.startswith('file://'):
            html = await asyncio.to_thread(Path(source[7:]).read_text, encoding='utf-8')
            log.info('Source read from file-url', extra={'source': source, 'bytes': len(html), 'duration_s': round(time.perf_counter() - t0, 3)})
            return source, html

        if source.startswith('http://') or source.startswith('https://'):
            r = await client.get(source, timeout=20)
            r.raise_for_status()
            html = r.text
            log.info('Source fetched', extra={'source': source, 'status': r.status_code, 'bytes': len(html), 'duration_s': round(time.perf_counter() - t0, 3)})
            return source, html

        html = await asyncio.to_thread(Path(source).read_text, encoding='utf-8')
        log.info('Source read from file', extra={'source': source, 'bytes': len(html), 'duration_s': round(time.perf_counter() - t0, 3)})
        return source, html
    except Exception:
        log.exception('Fetch failed', extra={'source': source})
        raise


async def extract_async(sources: Iterable[str], day_label: str | None = None) -> dict[str, Any]:
    src_list = list(sources)
    log.info('Extract start', extra={'sources': src_list, 'filter_day_label': day_label})

    async with httpx.AsyncClient(follow_redirects=True) as client:
        fetched = await asyncio.gather(*[_fetch_one(client, s) for s in src_list])

    t0 = time.perf_counter()
    parsed_batches = await asyncio.gather(*[asyncio.to_thread(parse_menu, html) for _, html in fetched])
    parse_dt = round(time.perf_counter() - t0, 3)

    meals = [m for batch in parsed_batches for m in batch]
    total_before = len(meals)

    if day_label:
        dl = day_label.strip()
        meals = [m for m in meals if m.day_label.strip() == dl]

    log.info(
        'Extract done',
        extra={
            'total_meals': total_before,
            'filtered_meals': len(meals),
            'parse_duration_s': parse_dt,
        },
    )

    return {
        'sources': src_list,
        'count': len(meals),
        'meals': [asdict(m) for m in meals],
    }


if __name__ == '__main__':
    out = asyncio.run(extract_async(
        ['https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/'],
        day_label=None,
    ))
    print(json.dumps(out, ensure_ascii=False, indent=2))
