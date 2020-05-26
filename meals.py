from ingredient import Ingredient

class Meal(Ingredient):
    def __init__(self,name,ingredient_name,quantity,recipe_description,prep_time,last_time_used,course,category,calories,proteins,carbohydrates,fats):
        super().__init__(ingredient_name,category,calories,proteins,carbohydrates,fats)
        self.name = name
        self.quantity = quantity
        self.recipe_description = recipe_description
        self.prep_time = prep_time
        self.last_time_used = last_time_used
        self.course = course
        self.calories = calories
        self.proteins = proteins
        self.carbohydrates = carbohydrates
        self.fats = fats

    def __str__(self):
        return 'Meal Name: {}\n Ingredients: {}\n Quantity: {}\n Recipe_desc: {}\n Prepare time: {}\n \
Last time used: {}\n Course: {}\n Calories: {}\n Proteins: {}\n Carbohydrates: {}\n Fats: {}'.format(
    self.name, self.ingredient_name, self.quantity, self.recipe_description, self.prep_time,
    self.last_time_used, self.course,self.calories,self.proteins,self.carbohydrates,self.fats)