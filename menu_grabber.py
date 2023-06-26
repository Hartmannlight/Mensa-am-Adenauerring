import datetime

import discord
from selenium import webdriver
from selenium.common import NoSuchElementException
from menu import Menu, Meal, Diet, Line

plan = {}

# a meal is one thing you can take at a line
# a line is a queue for a specific collection of meals
# a menu is a collection of all lines for a specific day
# a plan is a collection of all menus for one week


def get_menu(date: datetime.date):
    if date in plan:
        return plan[date]
    else:
        return plan[datetime.date.today()]


def get_menu_embed(date):
    menu = get_menu(date)

    embed = discord.Embed(title="Mensaeinheitsbrei der Mensa am Adenauerring - " + date.strftime("%A %d.%m.%Y"), color=0xff2f00)
    embed.set_footer(text="🍖 Fleisch, 🐟 Fisch, 🌱 Vegetarisch, 🌻 Vegan")

    embed.add_field(name="Linie 1 Gut & Günstig", value=menu.lines[0].text)
    embed.add_field(name="Linie 2 Vegane Linie", value=menu.lines[1].text)
    embed.add_field(name="Linie 3", value=menu.lines[2].text)
    embed.add_field(name="Linie 4", value=menu.lines[3].text)
    embed.add_field(name="Linie 5", value=menu.lines[4].text)
    embed.add_field(name="Linie 6", value=menu.lines[6].text)
    embed.add_field(name="[pizza]werk", value=menu.lines[12].text + "\n" + menu.lines[10].text)
    return embed


def update_menu(date: datetime.date):

    driver = get_selenium_menu(date)

    for day in range(1, 6):
        driver.execute_script(f"setCanteenDiv({day});")  # select the right tab for the current day

        menu = driver.find_element(by="id", value=f"canteen_day_{day}")

        line_objects = update_menu_text(menu)
        screenshot = update_screenshot(driver=driver, menu=menu)

        current_date = date + datetime.timedelta(days=day - 1)
        plan[current_date] = (Menu(line_objects, screenshot))

    driver.quit()


def update_screenshot(driver: webdriver.Chrome, menu):

    row = menu.find_elements(by="class name", value="mensatype_rows")

    # remove information that nobody needs (screenshots are too big to display them lossless on discord otherwise)
    driver.execute_script("arguments[0].remove()", row[5])
    driver.execute_script("arguments[0].remove()", row[6])
    driver.execute_script("arguments[0].remove()", row[7])
    driver.execute_script("arguments[0].remove()", row[8])
    driver.execute_script("arguments[0].remove()", row[9])
    driver.execute_script("arguments[0].remove()", row[11])

    # switch to dark mode
    driver.execute_script("""
        document.querySelectorAll('.page').forEach(icon => icon.style.setProperty('background-color', '#313338', 'important'));
        document.querySelectorAll('td').forEach(icon => icon.style.setProperty('background-color', '#313338', 'important'));
        document.querySelectorAll('td.mtd-icon div').forEach(icon => icon.style.setProperty('background-color', '#313338', 'important'));
        document.querySelectorAll('.bgp').forEach(icon => icon.style.setProperty('background-color', '#313338', 'important'));
        document.querySelectorAll('*').forEach(element => element.style.setProperty('color', '#dbdee1', 'important'));
    """)

    return menu.screenshot_as_png


def update_menu_text(menu):
    lines = menu.find_elements(by="class name", value="mensatype_rows")

    line_objects = []
    for line in lines:
        line_name = line.find_element(by="class name", value="mensatype").text
        text = ""

        meals_container = line.find_element(by="class name", value="meal-detail-table")  # remove?
        meals = meals_container.find_elements(by="tag name", value="tr")

        meal_objects = []
        for meal in meals:

            try:
                meal_title_container = meal.find_element(by="class name", value="menu-title")
            except NoSuchElementException:
                continue

            name = meal_title_container.find_element(by="class name", value="bg").text
            price = meal.find_element(by="class name", value="price_1").text
            diet = meal.get_attribute("class")
            diet_obj = Diet(diet)

            try:
                allergens = meal_title_container.find_element(by="tag name", value="sup").text
            except NoSuchElementException:
                allergens = ""

            meal_objects.append(Meal(name, price, diet_obj, allergens))
            text += f"{diet_obj.emoji} {name} **{price}**\n"

        line_objects.append(Line(name=line_name, meals=meal_objects, text=text))
    return line_objects


def get_selenium_menu(date: datetime.date):
    # setup and start automated Chrome browser
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # runs on server without display
    options.add_argument("--window-size=2000,5000")  # increase window size to prevent cut off screenshots
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')  # server has no gpu
    options.add_argument('--disable-dev-shm-usage')  # docker optimization(?)
    driver = webdriver.Chrome(options=options)

    kw = date.isocalendar()[1]
    driver.get(f"https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/?kw={kw}")
    return driver
