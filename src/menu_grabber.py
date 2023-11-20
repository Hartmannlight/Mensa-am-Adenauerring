import datetime
import logging

import aiohttp
from bs4 import BeautifulSoup

from menu import Diet, Meal, Line, Menu, NutriScore, EnvironmentScore

logger = logging.getLogger("bot")

# a meal is one thing you can take at a line
# a (canteen) line is a queue for a specific collection of meals
# a menu is a collection of all lines for a specific day
# a plan is a collection of all menus for one week


async def get_week_plan(week: int) -> dict[datetime.date, Menu]:

    if week + 1 > 52:
        next_week = 1
    else:
        next_week = week + 1

    logger.info(f'Getting plan updates for week {week} and {next_week}')

    html_plan_this_week = await get_html_plan(week)
    html_plan_next_week = await get_html_plan(next_week)

    today = datetime.date.today()
    weekday_number = today.weekday()
    days_left_this_week = 5 - weekday_number

    menus = {}
    for i in range(0, days_left_this_week):
        menu_object = await get_menu(html_plan_this_week, i + 1)

        current_day = today + datetime.timedelta(days=i)
        menus[current_day] = menu_object

    last_monday = today - datetime.timedelta(days=weekday_number)
    next_monday = last_monday + datetime.timedelta(days=7)
    today = next_monday

    for i in range(0, 5):
        menu_object = await get_menu(html_plan_next_week, i + 1)

        current_day = today + datetime.timedelta(days=i)
        menus[current_day] = menu_object

    return menus


async def get_html_plan(week: int) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/?kw={week}') as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            return soup


async def get_menu(html_plan: BeautifulSoup, day: int) -> Menu:

    html_menu = html_plan.find(id=f"canteen_day_{day}")  # day 1 = today, day 2 = tomorrow, etc.
    if html_menu is None: return Menu([])

    html_canteen_lines = html_menu.find_all(class_="mensatype_rows")
    if html_canteen_lines is None: return Menu([])

    canteen_line_objects = []
    for html_canteen_line in html_canteen_lines:
        line_name = html_canteen_line.find(class_="mensatype").get_text()  # "Linie 2 vegane Linie" e.g.
        meal_objects = await extract_meals(html_canteen_line.find(class_="meal-detail-table"))

        canteen_line_object = Line(line_name, meal_objects)
        canteen_line_objects.append(canteen_line_object)

    menu = Menu(canteen_line_objects)
    return menu


async def extract_meals(meals_html_container) -> list[Meal]:
    meal_objects = []
    meals = meals_html_container.find_all('tr')
    if meals is None: return meal_objects

    i = 0
    while i < len(meals):
        meal = meals[i]

        if meal.get("class") is None:  # in case a line is closed, the first element is empty
            return meal_objects

        meal_title_html_container = meal.find(class_="menu-title")
        name = meal_title_html_container.find(class_="bg").get_text()

        allergens = meal_title_html_container.find("sup")
        allergens = allergens.get_text() if allergens else None

        price = meal.find(class_="price_1").get_text()

        diet_text = meal.get("class")[0]
        diet = Diet(diet_text)

        i += 1

        nutri_score = None
        environment_score = None

        if i < len(meals):
            meal_nutri = meals[i]

            if meal_nutri.get("class") is None:
                energy = meal_nutri.find(class_="energie").find_all('div')[1].get_text()
                proteins = meal_nutri.find(class_="proteine").find_all('div')[1].get_text()
                carbohydrates = meal_nutri.find(class_="kohlenhydrate").find_all('div')[1].get_text()
                sugar = meal_nutri.find(class_="zucker").find_all('div')[1].get_text()
                fat = meal_nutri.find(class_="fett").find_all('div')[1].get_text()
                saturated_fat = meal_nutri.find(class_="gesaettigt").find_all('div')[1].get_text()
                salt = meal_nutri.find(class_="salz").find_all('div')[1].get_text()
                nutri_score = NutriScore(energy, proteins, carbohydrates, sugar, fat, saturated_fat, salt)

                if meal_nutri.find(class_="co2_bewertung_wolke"):
                    co2 = meal_nutri.find(class_="co2_bewertung_wolke").find(class_="value").get_text()
                else:
                    co2 = meal_nutri.find(class_="co2_bewertung").find(class_="value").get_text()

                water = meal_nutri.find(class_="wasser_bewertung").find(class_="value").get_text()
                animal_welfare = meal_nutri.find(class_="tierwohl").get("class")[1]
                rainforest = meal_nutri.find(class_="regenwald").get("class")[1]
                environment_score = EnvironmentScore(co2, water, animal_welfare, rainforest)

                i += 1

        meal_object = Meal(name, price, diet, nutri_score, environment_score, allergens)
        meal_objects.append(meal_object)

    return meal_objects
