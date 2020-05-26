class User(object):
    def __init__(self, name, weight, height, age, gender, target):
        self.name = name
        self.weight = weight
        self.height = height
        self.age = age
        self.gender = gender
        self.target = target

    @property
    def BMR(self):
        if self.gender == "Male":
            return ((9.99*self.weight)+(6.25*self.height)+(4.92*self.age)+5+400)
        else:
            return ((9.99*self.weight)+(6.25*self.height)+(4.92*self.age)-161+400)

    @property
    def calories(self):
        if self.target == 'reduction':
            kcal = self.BMR + self.BMR*0.1 - 100
            return kcal
        elif self.target == 'mass':
            kcal = self.BMR + self.BMR*0.1 + 300
            return kcal
        else:
            kcal = self.BMR + self.BMR*0.1
            return round(kcal,1)
    @property
    def makro(self):
        proteins = self.weight*1.2
        proteins_kcal = proteins * 4
        fat = self.weight*1.5
        fat_kcal = fat * 9
        proteins_and_fat = proteins_kcal + fat_kcal
        kcal_left = self.calories - proteins_and_fat
        carbs = kcal_left/4
        carbs_kcal = carbs*4
        total_kcal = carbs_kcal+proteins_and_fat
        return round(proteins,1), str(round(carbs,1)), round(fat,1) 

    def __str__(self):
        return self.name





