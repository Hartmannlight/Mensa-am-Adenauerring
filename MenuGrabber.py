from selenium import webdriver


class Menu:
    def __init__(self):
        self.text = []  # menu[line_number][meal_number]: str
        self.screenshot = None

    def update(self):
        # setup and start automated Chrome browser
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # runs on server without display
        options.add_argument("--window-size=2000,5000")  # increase window size to prevent cut off screenshots
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')  # server has no gpu
        options.add_argument('--disable-dev-shm-usage')  # docker optimization(?)
        driver = webdriver.Chrome(options=options)

        driver.get("https://www.sw-ka.de/de/hochschulgastronomie/speiseplan/mensa_adenauerring/")

        self.update_text(driver)
        self.update_screenshot(driver)

        driver.quit()

    def update_text(self, driver: webdriver.Chrome):
        self.text = []  # wipe old menu
        line = driver.find_elements(by="class name", value="meal-detail-table")

        for line_number in range(13):  # there are just 13 lines, and we want to cut off everything that comes after that
            self.text.append([])  # create dimension for meals [line_number][meal_number]
            meal = line[line_number].find_elements(by="tag name", value="tr")

            for meal_number in range(len(meal)):
                diet = meal[meal_number].get_attribute("class")

                if diet == "mt-0":  # animal rennet
                    prefix = ""
                elif diet == "mt-1":  # pork
                    prefix = "🍖 "
                elif diet == "mt-2":  # beef
                    prefix = "🍖 "
                elif diet == "mt-3":  # fish
                    prefix = "🐟 "
                elif diet == "mt-4":  # ?
                    prefix = ""
                elif diet == "mt-5":  # ?
                    prefix = ""
                elif diet == "mt-6":  # vegan
                    prefix = "🌻 "
                elif diet == "mt-7":  # vegetarian
                    prefix = "🌱 "
                elif diet == "mt-8":  # ?
                    prefix = ""
                elif diet == "mt-9":  # ?
                    prefix = ""
                else:
                    continue

                # remove allergen information
                sub_elements = line[line_number].find_elements(by="tag name", value="sup")
                for sub_element in sub_elements:
                    driver.execute_script("arguments[0].remove()", sub_element)

                # store and return meal description
                meal_text = meal[meal_number].text
                self.text[line_number].append(prefix + meal_text)

    def update_screenshot(self, driver: webdriver.Chrome):

        page = driver.find_element(by="id", value="canteen_day_1")
        row = page.find_elements(by="class name", value="mensatype_rows")

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

        self.screenshot = page.screenshot_as_png
