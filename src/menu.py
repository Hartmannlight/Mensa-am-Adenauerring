
class NutriScore:
    def __init__(self, energy, proteins, carbohydrates, sugar, fat, saturated_fat, salt):
        self.energy = energy
        self.proteins = proteins
        self.carbohydrates = carbohydrates
        self.sugar = sugar
        self.fat = fat
        self.saturated_fat = saturated_fat
        self.salt = salt

    def __str__(self):
        text = f"Energie: {self.energy}\n"
        text += f"Proteine: {self.proteins}\n"
        text += f"Kohlenhydrate: {self.carbohydrates}\n"
        text += f"Zucker: {self.sugar}\n"
        text += f"Fett: {self.fat}\n"
        text += f"Gesättigte Fettsäuren: {self.saturated_fat}\n"
        text += f"Salz: {self.salt}\n"
        return text


class EnvironmentScore:
    def __init__(self, co2: int, water: float, animal_welfare: int, rainforest: int):
        self.co2 = co2
        self.water = water

        if animal_welfare == "tierwohl_1":
            self.animal_welfare = "Schlechte Haltungsbedingungen"
        elif animal_welfare == "tierwohl_2":
            self.animal_welfare = "Regional"
        elif animal_welfare == "tierwohl_3":
            self.animal_welfare = "Artgerechte Haltung"

        if rainforest == "regenwald_1":
            self.rainforest = "Nicht geschützt"
        elif rainforest == "regenwald_2":
            self.rainforest = "Teilweise geschützt"
        elif rainforest == "regenwald_3":
            self.rainforest = "Geschützt"

    def __str__(self):
        text = f"CO2: {self.co2}\n"
        text += f"Wasser: {self.water}\n"
        text += f"Tierwohl: {self.animal_welfare}\n"
        text += f"Regenwald: {self.rainforest}\n"
        return text


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
    def __init__(self, name: str, price: str, diet: Diet, nutri_score: NutriScore | None, environment_score: EnvironmentScore | None, allergens: str | None):
        self.name = name
        self.price = price
        self.diet = diet
        self.nutri_score = nutri_score
        self.environmental_score = environment_score
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
