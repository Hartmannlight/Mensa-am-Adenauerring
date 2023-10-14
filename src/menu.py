
class Diet:
    def __init__(self, abbreviation: str):
        if abbreviation == "mt-0":  # animal rennet
            self.emoji = ""
        elif abbreviation == "mt-1":  # pork
            self.emoji = "🍖 "
        elif abbreviation == "mt-2":  # beef
            self.emoji = "🍖 "
        elif abbreviation == "mt-3":  # fish
            self.emoji = "🐟 "
        elif abbreviation == "mt-4":  # ?
            self.emoji = ""
        elif abbreviation == "mt-5":  # ?
            self.emoji = ""
        elif abbreviation == "mt-6":  # vegan
            self.emoji = "🌻 "
        elif abbreviation == "mt-7":  # vegetarian
            self.emoji = "🌱 "
        elif abbreviation == "mt-8":  # ?
            self.emoji = ""
        elif abbreviation == "mt-9":  # ?
            self.emoji = ""
        else:
            self.emoji = ""


class Meal:
    def __init__(self, name: str, price: str, diet: Diet, allergens: str):
        self.name = name
        self.price = price
        self.diet = diet
        self.allergens = allergens

    def __str__(self):
        text = f"{self.diet.emoji} {self.name}"

        if self.price != "":
            text += f" **{self.price}**"

        text += "\n"
        return text


class Line:
    def __init__(self, name: str, meals: list[Meal]):
        self.name = name
        self.meals = meals

    def __str__(self):

        if not self.meals:
            return "*Geschlossen*\n"

        text = ""
        for meal in self.meals:
            text += str(meal)
        return text


class Menu:
    def __init__(self, lines: list[Line]):
        self.lines = lines

    def __str__(self):
        text = ""
        for line in self.lines:
            text += f"**__{str(line.name)}__**:\n"
            text += str(line) + "\n\n"
        return text
