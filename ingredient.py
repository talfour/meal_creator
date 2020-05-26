class Ingredient(object):
    def __init__(self, ingredient_name, category, calories, proteins, carbohydrates, fats):
        self.ingredient_name = ingredient_name
        self.category = category
        self.calories = calories / 100
        self.proteins = proteins / 100
        self.carbohydrates = carbohydrates / 100
        self.fats = fats / 100

    def __str__(self):
        return 'Name: {}\n Category: {}\n kcal: {}\n proteins: {}\n carbs: {}\n fats: {}'.format(self.ingredient_name, self.category, self.calories, self.proteins, self.carbohydrates, self.fats)
        
    