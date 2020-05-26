import sys, os, json, sqlite3, numbers, random
import qdarkgraystyle
from datetime import date
from more_itertools import roundrobin
from PyQt5 import QtWidgets, uic, QtCore
from user import User
from dbcon import DatabaseManger
from meals import Meal
from ingredient import Ingredient

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('mainscreen.ui', self)
        self.setStyleSheet(qdarkgraystyle.load_stylesheet())
        self.comboBoxNames = self.findChild(QtWidgets.QComboBox, 'comboBoxNames')
        self.loginBtn = self.findChild(QtWidgets.QPushButton, 'loginBtn')
        self.registerBtn = self.findChild(QtWidgets.QPushButton, 'registerBtn')
        self.loginBtn.clicked.connect(self.login_user)
        self.registerBtn.clicked.connect(self.register_new_user)
        self.populate_combo()
        self.show()

    def populate_combo(self):
        users = dbmg.get_all_users()
        self.comboBoxNames.clear()
        for user in users:
            self.comboBoxNames.addItem(user['name'])
    
    def login_user(self):
        self.loggedUser = LoggedIn(self.comboBoxNames.currentText())#argument which is passing choosen user
        self.loggedUser.show()
        self.hide()
        return self.loggedUser
        
    def register_new_user(self):
        self.windowregister = RegisterUser()
        self.windowregister.show()

    def message(self,title,text,icon=None):     
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        x = msg.exec_()
    
    
class RegisterUser(QtWidgets.QWidget):
    def __init__(self):
        super(RegisterUser, self).__init__()
        uic.loadUi('registeruser.ui',self)
        self.setStyleSheet(qdarkgraystyle.load_stylesheet())
        self.textName = self.findChild(QtWidgets.QLineEdit, 'nameLine')
        self.weightLine = self.findChild(QtWidgets.QLineEdit, 'weightLine')
        self.heightLine = self.findChild(QtWidgets.QLineEdit, 'heightLine')
        self.ageLine = self.findChild(QtWidgets.QLineEdit, 'ageLine')
        self.comboTarget = self.findChild(QtWidgets.QComboBox, 'targetCombo')
        self.comboGender = self.findChild(QtWidgets.QComboBox, 'genderCombo')
        self.comboTarget.addItems(['reduction', 'keep weight', 'mass'])
        self.comboGender.addItems(['Male', 'Female'])
        self.addNewUserBtn = self.findChild(QtWidgets.QPushButton, 'addNewUserBtn')
        self.addNewUserBtn.clicked.connect(self.get_text)

    def get_text(self):
            name = self.textName.text()
            weight = self.weightLine.text()
            height= self.heightLine.text()
            age = self.ageLine.text()
            target = self.comboTarget.currentText()
            gender = self.comboGender.currentText()
            if name and weight and height and age is not None:
                if weight.isdigit() and height.isdigit() and age.isdigit():
                    try:
                        dbmg.create_user_and_his_week(name, weight, height, age, gender, target)    
                        Ui.message(RegisterUser, 'New user', "New user is now created.")
                        window.populate_combo()
                        self.hide()
                    except sqlite3.IntegrityError:
                        Ui.message(RegisterUser, 'Warrning', "User with this name is already created. Try different name.")
                else:
                    Ui.message(RegisterUser, 'Warning', "Weight, height, age - please enter numbers.")      
            else:
                Ui.message(RegisterUser, 'New user', "Please fill all data.")   

class LoggedIn(QtWidgets.QWidget):
    def __init__(self, user):
        super(LoggedIn, self).__init__()
        self.setStyleSheet(qdarkgraystyle.load_stylesheet())
        uic.loadUi('after_login.ui',self)
        self.userName = user
        dbmg = DatabaseManger('dbmeal.db')
        user_data = dbmg.get_user_byname(self.userName)
        self.new_user = User(user_data[0][1],user_data[0][2],user_data[0][3],user_data[0][4],user_data[0][5],user_data[0][6])
        self.populate_table()
        self.populate_combo_cat()
        self.add_products_to_search()
        self.populate_ingredients()
        self.populate_meals() 
        self.your_day_data(self.new_user)
        self.update_meals_in_user_day_on_load()
        
        #YOURDAY
        self.yourDayUserName = self.findChild(QtWidgets.QLabel, 'yourdayUsername')
        self.yourDayUserName.setText(self.userName)
        self.yourdayMaxCalories = self.findChild(QtWidgets.QLabel, 'yourdayMaxCalories')
        self.yourdayProteins = self.findChild(QtWidgets.QLabel, 'yourdayProteins')
        self.yourdayCarbohydrates = self.findChild(QtWidgets.QLabel, 'yourdayCarbohydrates')
        self.yourdayFats = self.findChild(QtWidgets.QLabel, 'yourdayFats')
        self.choosenDay = self.findChild(QtWidgets.QComboBox, 'choosenDay')
        self.checkDayPlan = self.findChild(QtWidgets.QPushButton, 'checkDayPlan')
        self.checkDayPlan.clicked.connect(self.selected_day)
        self.mondayMealOne = self.findChild(QtWidgets.QLabel, 'mondayMealOne')
        self.mondayMealTwo = self.findChild(QtWidgets.QLabel, 'mondayMealTwo')
        self.mondayMealThree = self.findChild(QtWidgets.QLabel, 'mondayMealThree')
        self.mondayMealFour = self.findChild(QtWidgets.QLabel, 'mondayMealFour')
        self.mondayMealFive = self.findChild(QtWidgets.QLabel, 'mondayMealFive')
        self.mondayTotal = self.findChild(QtWidgets.QLabel, 'mondayTotal')
        self.tuesdayMealOne = self.findChild(QtWidgets.QLabel, 'tuesdayMealOne')
        self.tuesdayMealTwo = self.findChild(QtWidgets.QLabel, 'tuesdayMealTwo')
        self.tuesdayMealThree = self.findChild(QtWidgets.QLabel, 'tuesdayMealThree')
        self.tuesdayMealFour = self.findChild(QtWidgets.QLabel, 'tuesdayMealFour')
        self.tuesdayMealFive = self.findChild(QtWidgets.QLabel, 'tuesdayMealFive')
        self.tuesdayTotal = self.findChild(QtWidgets.QLabel, 'tuesdayTotal')
        self.wednesdayMealOne = self.findChild(QtWidgets.QLabel, 'wednesdayMealOne')
        self.wednesdayMealTwo = self.findChild(QtWidgets.QLabel, 'wednesdayMealTwo')
        self.wednesdayMealThree = self.findChild(QtWidgets.QLabel, 'wednesdayMealThree')
        self.wednesdayMealFour = self.findChild(QtWidgets.QLabel, 'wednesdayMealFour')
        self.wednesdayMealFive = self.findChild(QtWidgets.QLabel, 'wednesdayMealFive')
        self.wednesdayTotal = self.findChild(QtWidgets.QLabel, 'wednesdayTotal')
        self.thursdayMealOne = self.findChild(QtWidgets.QLabel, 'thursdayMealOne')
        self.thursdayMealTwo = self.findChild(QtWidgets.QLabel, 'thursdayMealTwo')
        self.thursdayMealThree = self.findChild(QtWidgets.QLabel, 'thursdayMealThree')
        self.thursdayMealFour = self.findChild(QtWidgets.QLabel, 'thursdayMealFour')
        self.thursdayMealFive = self.findChild(QtWidgets.QLabel, 'thursdayMealFive')
        self.thursdayTotal = self.findChild(QtWidgets.QLabel, 'thursdayTotal')
        self.fridayMealOne = self.findChild(QtWidgets.QLabel, 'fridayMealOne')
        self.fridayMealTwo = self.findChild(QtWidgets.QLabel, 'fridayMealTwo')
        self.fridayMealThree = self.findChild(QtWidgets.QLabel, 'fridayMealThree')
        self.fridayMealFour = self.findChild(QtWidgets.QLabel, 'fridayMealFour')
        self.fridayMealFive = self.findChild(QtWidgets.QLabel, 'fridayMealFive')
        self.fridayTotal = self.findChild(QtWidgets.QLabel, 'fridayTotal')
        self.saturdayMealOne = self.findChild(QtWidgets.QLabel, 'saturdayMealOne')
        self.saturdayMealTwo = self.findChild(QtWidgets.QLabel, 'saturdayMealTwo')
        self.saturdayMealThree = self.findChild(QtWidgets.QLabel, 'saturdayMealThree')
        self.saturdayMealFour = self.findChild(QtWidgets.QLabel, 'saturdayMealFour')
        self.saturdayMealFive = self.findChild(QtWidgets.QLabel, 'saturdayMealFive')
        self.saturdayTotal = self.findChild(QtWidgets.QLabel, 'saturdayTotal')
        self.sundayMealOne = self.findChild(QtWidgets.QLabel, 'sundayMealOne')
        self.sundayMealTwo = self.findChild(QtWidgets.QLabel, 'sundayMealTwo')
        self.sundayMealThree = self.findChild(QtWidgets.QLabel, 'sundayMealThree')
        self.sundayMealFour = self.findChild(QtWidgets.QLabel, 'sundayMealFour')
        self.sundayMealFive = self.findChild(QtWidgets.QLabel, 'sundayMealFive')
        self.sundayTotal = self.findChild(QtWidgets.QLabel, 'sundayTotal')

        #PRODUCT LIST
        self.foodNameText = self.findChild(QtWidgets.QLineEdit, 'foodNameText')
        self.categoryComboBox = self.findChild(QtWidgets.QComboBox, 'categoryComboBox')
        self.categoryComboBox.setEditable(True)
        self.caloriesText = self.findChild(QtWidgets.QLineEdit, 'caloriesText')
        self.proteinsText = self.findChild(QtWidgets.QLineEdit, 'proteinsText')
        self.carbohydratesText = self.findChild(QtWidgets.QLineEdit, 'carbohydratesText')
        self.fatText = self.findChild(QtWidgets.QLineEdit, 'fatText')
        self.addProductButton = self.findChild(QtWidgets.QPushButton, 'addProductButton')
        self.addProductButton.clicked.connect(self.add_product)
        self.tableFood = self.findChild(QtWidgets.QTableWidget, 'tableFood')        
        self.deleteProductButton = self.findChild(QtWidgets.QPushButton, 'deleteProductButton')
        self.deleteProductButton.clicked.connect(self.delete_product)

        #RANDOM MEAL
        self.randomMealName = self.findChild(QtWidgets.QLabel, 'randomMealName')
        self.randomLastTimeUsed = self.findChild(QtWidgets.QLabel, 'randomLastTimeUsed')
        self.randomProteinsCarbsFat = self.findChild(QtWidgets.QLabel, 'randomProteinsCarbsFat')
        self.randomPrepareTime = self.findChild(QtWidgets.QLabel, 'randomPrepareTime')
        self.randomListIngredients = self.findChild(QtWidgets.QTableWidget, 'randomListIngredients')
        self.randomRecipe = self.findChild(QtWidgets.QPlainTextEdit, 'randomRecipe')
        self.randomCalories = self.findChild(QtWidgets.QLabel, 'randomCalories')
        self.randomRandomizeButton = self.findChild(QtWidgets.QPushButton, 'randomRandomizeButton')
        self.randomRandomizeButton.clicked.connect(self.randomize_meal)
        self.randomAcceptButton = self.findChild(QtWidgets.QPushButton, 'randomAcceptButton')
        self.randomAcceptButton.clicked.connect(self.accept_current_meal)

        #MEALS
        self.mealsMealName = self.findChild(QtWidgets.QLineEdit, 'mealsMealName')
        self.mealsIngredients = self.findChild(QtWidgets.QComboBox, 'mealsIngredients')
        self.mealsReceipe = self.findChild(QtWidgets.QPlainTextEdit, 'mealsReceipe')
        self.mealsPrepareTime = self.findChild(QtWidgets.QLineEdit, 'mealsPrepareTime')
        self.mealsAddMealBtn = self.findChild(QtWidgets.QPushButton, 'mealsAddMealBtn')
        self.mealsAddMealBtn.clicked.connect(self.add_meal)
        self.mealsList = self.findChild(QtWidgets.QListWidget, 'mealsList')
        self.mealsAddIngredient = self.findChild(QtWidgets.QPushButton, 'mealsAddIngredient')
        self.mealsAddIngredient.clicked.connect(self.add_meal_ingredient_to_list)
        self.mealsDeleteIngredient = self.findChild(QtWidgets.QPushButton, 'mealsDeleteIngredient')
        self.mealsDeleteIngredient.clicked.connect(self.delete_meal_ingredient_from_list)
        self.mealsIngredientsList = self.findChild(QtWidgets.QTableWidget, 'mealsIngredientsList')
        self.mealsAmount = self.findChild(QtWidgets.QLineEdit, 'mealsAmount')
        self.mealsList.itemDoubleClicked.connect(self.select_meal_for_info)
        
        #USER INFO
        self.userWeight = self.findChild(QtWidgets.QLineEdit,'userWeight')
        self.userWeight.setPlaceholderText(str("Current: {}".format(self.new_user.weight)))
        self.userAge = self.findChild(QtWidgets.QLineEdit,'userAge')
        self.userAge.setPlaceholderText(str("Current: {}".format(self.new_user.age)))
        self.userTarget = self.findChild(QtWidgets.QComboBox,'userTarget')
        self.userTarget.currentIndex()
        self.userTarget.setCurrentText(str(self.new_user.target))
        self.userApplyBtn = self.findChild(QtWidgets.QPushButton, 'userApplyBtn')
        self.userApplyBtn.clicked.connect(self.change_user_data)

        #SEARCH MEAL
        self.searchNewProduct = self.findChild(QtWidgets.QComboBox, 'searchNewProduct')
        self.searchAdd = self.findChild(QtWidgets.QPushButton,'searchAdd')
        self.searchList = self.findChild(QtWidgets.QListWidget, 'searchList')
        self.searchDelete = self.findChild(QtWidgets.QPushButton,'searchDelete')
        self.searchGenerateMeal = self.findChild(QtWidgets.QPushButton,'searchGenerateMeal')
        self.searchProducts = self.findChild(QtWidgets.QTableWidget,'searchProducts')
        self.searchReceipe = self.findChild(QtWidgets.QPlainTextEdit,'searchReceipe')
        self.searchProteinsCarbsFats = self.findChild(QtWidgets.QLabel,'searchProteinsCarbsFats')
        self.searchPrepareTime = self.findChild(QtWidgets.QLabel,'searchPrepareTime')
        self.searchKcal = self.findChild(QtWidgets.QLabel,'searchKcal')
        self.searchAdd.clicked.connect(self.find_meal_addBtn)
        self.searchGenerateMeal.clicked.connect(self.find_meal)
        self.searchDelete.clicked.connect(self.delete_button)
        self.searchChoicesMeal = self.findChild(QtWidgets.QComboBox, 'searchChoicesMeal')
        self.searchChoicesMeal.currentTextChanged.connect(self.combo_on_box_changed)

    def populate_combo_cat(self):
        dbmg = DatabaseManger('dbmeal.db')
        categories = dbmg.get_food_categories()
        for cat in categories:
            self.categoryComboBox.addItems(cat)
        dbmg.conn.close()

    def your_day_data(self,new_user):
        dbmg = DatabaseManger('dbmeal.db')
        user_data = dbmg.get_user_byname(self.userName)
        self.yourdayMaxCalories.setText("Max calories: {} kcal".format(str((new_user.calories))[:4]))
        self.yourdayProteins.setText("Max proteins: {}g".format(new_user.makro[0]))
        self.yourdayCarbohydrates.setText("Max carbohydrates: {}g".format(new_user.makro[1]))
        self.yourdayFats.setText("Max fats: {}g".format(new_user.makro[2]))
        return new_user, user_data
        dbmg.conn.close()

    def populate_table(self):
        product_dbmg = DatabaseManger("dbmeal.db")
        test = product_dbmg.get_all_products()
        self.tableFood.setRowCount(1)
        for row, form in enumerate(test):
            self.tableFood.insertRow(row)
            for column, item in enumerate(form):
                cellinfo = QtWidgets.QTableWidgetItem(str(item))
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableFood.setItem(row,column, cellinfo)
        product_dbmg.conn.close()

    def delete_product(self):
        table = self.tableFood.selectedItems()
        to_delete = None
        for item in table:
            to_delete = item.text()
        if to_delete.isdigit():
            resp = QtWidgets.QMessageBox.question(self, 'Attention', 'Are you sure that you want to delete ingredient with id {} ? You cannot change it later.'.format(to_delete),
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
            if resp == QtWidgets.QMessageBox.Yes:
                con = dbmg.delete_product(to_delete)
                self.populate_table()
                Ui.message(LoggedIn, 'Information', "Ingredient deleted.")  
            else:
                return
            
    def add_product(self):
        name = self.foodNameText.text()
        category = self.categoryComboBox.currentText()
        energy = self.caloriesText.text()
        protein = self.proteinsText.text()
        carbohydrates = self.carbohydratesText.text()
        fat = self.fatText.text()
        if name and category and energy and protein and carbohydrates and fat is not None:
            if energy.isdigit() and protein.isdigit() and carbohydrates.isdigit() and fat.isdigit():
                try:
                    resp = QtWidgets.QMessageBox.question(self, 'Attention', 'Are you sure that you want to add product with this values ? You cannot change it later.',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
                    if resp == QtWidgets.QMessageBox.Yes:
                        product_add_manager = DatabaseManger("dbmeal.db")
                        product_add_manager.add_product(name.capitalize(),category.capitalize(),energy,protein,carbohydrates,fat)
                        self.populate_table()
                        self.populate_ingredients()
                        Ui.message(LoggedIn, 'New product', "Added successful.")  
                        product_add_manager.conn.close()
                    else:
                        return
                except sqlite3.IntegrityError:
                    Ui.message(LoggedIn, "Warning", "Product with this name is already in database.")  
            else:
                Ui.message(LoggedIn, 'New product', "Energy, proteins, carbohydrates and fats must contain numbers only dont use float numbers.")                  
        else:
            Ui.message(LoggedIn, 'New product', "Oups are you sure you have filled up all boxes ?")
 
    def randomize_meal(self):
        dbmg = DatabaseManger("dbmeal.db")
        random_meal = random.choice(dbmg.get_all_meals_to_randomize())
        meal_id = dbmg.get_meal_by_id(random_meal[0])
        sum_carbs = 0; sum_fat = 0; sum_proteins = 0; sum_kcal = 0
        product_list = []
        quantity_list = []
        calories = 0
        proteins = 0
        carbs = 0
        fat = 0

        for meal in range(len(meal_id)):
            quantity = meal_id[meal][9]
            ingredient = meal_id[meal][4]
            fat += meal_id[meal][3]*meal_id[meal][9]/100
            proteins += meal_id[meal][5]*meal_id[meal][9]/100
            carbs += meal_id[meal][7]*meal_id[meal][9]/100
            calories += meal_id[meal][11]*meal_id[meal][9]/100
            product_list.append(ingredient)
            quantity_list.append(quantity)
        meal = Meal(meal_id[0][0],product_list,quantity_list,meal_id[0][10],meal_id[0][1],meal_id[0][2],None,None,round(calories,1),round(proteins,1),round(carbs,1),round(fat,1))

        self.randomListIngredients.setRowCount(0)
        for row, item in enumerate(product_list):
            self.randomListIngredients.insertRow(row)
            for i in range(0,len(product_list)):
                cell_info = QtWidgets.QTableWidgetItem(str(item))
                self.randomListIngredients.setItem(row, 0, cell_info )
        for row, item in enumerate(quantity_list):
            for i in range(0,len(quantity_list)):
                cell_info = QtWidgets.QTableWidgetItem(str(item))
                self.randomListIngredients.setItem(row, 1, cell_info)

        self.randomMealName.setText(meal.name.capitalize())
        self.randomRecipe.setPlainText("Recipe:\n{}".format(meal.recipe_description))
        self.randomCalories.setText("Calories: {}".format(meal.calories))
        self.randomPrepareTime.setText(str("Prepare time: {}".format(meal.prep_time)))
        self.randomLastTimeUsed.setText("Last time used: {}".format(meal.last_time_used))
        self.randomProteinsCarbsFat.setText("Proteins: {} \nCarbohydrates: {} \nFats: {}".format(meal.proteins,meal.carbohydrates,meal.fats))
        self.current_meal = random_meal
        dbmg.conn.close()
        return random_meal
        
    def accept_current_meal(self):
        current_meal = self.current_meal
        today = date.today()
        dbmg = DatabaseManger("dbmeal.db")
        dbmg.update_date(current_meal[0],today)
        dbmg.conn.close()
        return self.randomLastTimeUsed.clear(), self.randomLastTimeUsed.setText("Last time used: {}".format(today)) #current_meal[5])
        

    def populate_ingredients(self):
        dbmg = DatabaseManger("dbmeal.db")
        ingredients = dbmg.get_all_ingredients()
        for ingredient in ingredients:
            self.mealsIngredients.addItems(ingredient) 
        dbmg.conn.close()

    def add_meal_ingredient_to_list(self):
        ingredients = self.mealsIngredients.currentText()
        quantity = self.mealsAmount.text()
        n = self.mealsIngredientsList.rowCount()
        self.mealsIngredientsList.setRowCount(n)
        self.mealsIngredientsList.insertRow(0)

        cell_info = QtWidgets.QTableWidgetItem(str(ingredients))
        cell_info_quantity = QtWidgets.QTableWidgetItem(str(quantity))
        self.mealsIngredientsList.setItem(0,0,cell_info)
        self.mealsIngredientsList.setItem(0,1,cell_info_quantity)
        text_item = self.mealsIngredientsList.item(0,0).text()
    
    def delete_meal_ingredient_from_list(self):
        table = self.mealsIngredientsList.selectedItems()
        for index in sorted(table):
            self.mealsIngredientsList.removeRow(index.row())

    def add_meal(self):
        dbmg = DatabaseManger("dbmeal.db")
        last_id = dbmg.check_last_id()
        meal_name = self.mealsMealName.text()
        receipe = self.mealsReceipe.toPlainText()
        prepare_time = self.mealsPrepareTime.text()
        ingredient_list = []
        quantity_list = []
        both_lists = []
        column_count = self.mealsIngredientsList.columnCount()
        row_count = self.mealsIngredientsList.rowCount()

        for row in range(row_count):
            for col in range(column_count):
                item = self.mealsIngredientsList.item(row,col)
                item_text = item.text()
                if col == 1:
                    quantity_list.append(item_text)
                else:
                    ingredient_list.append(item_text)
        
        both_lists.append(ingredient_list)
        both_lists.append(quantity_list)
        ingredient_length = len(ingredient_list)
        rows_to_append = [x for x in range((last_id[0][0]+1), (last_id[0][0]+ingredient_length+1))]
        both_lists.append(rows_to_append)
        zipped = []

        for each in zip(*both_lists):
            zipped.append(each)

        all_meals = dbmg.get_all_meals()

        try:
            dbmg.add_meal(meal_name,zipped,ingredient_list,quantity_list,receipe,prepare_time)
            self.mealsMealName.clear()
            self.mealsAmount.clear()
            self.mealsReceipe.clear()
            self.mealsPrepareTime.clear()
            self.mealsIngredientsList.setRowCount(0)

        except sqlite3.IntegrityError:
            Ui.message(LoggedIn, "Warning", "Meal with this name is already in database. Please try to use different name.")  
        dbmg.conn.close()
        self.populate_meals()

    def populate_meals(self):
        self.mealsList.clear()
        meal_dbmg = DatabaseManger("dbmeal.db")
        all_meals = meal_dbmg.get_all_meals()
        for item in all_meals:
            self.mealsList.addItem(item[0])
        meal_dbmg.conn.close()

    def change_user_data(self):
        weight = self.userWeight.text()
        age = self.userAge.text()
        target = self.userTarget.currentText()
        user_dbmg = DatabaseManger('dbmeal.db')
        if weight != "" and weight.isdigit():
            user_dbmg.update_weight(int(weight), self.userName)
            Ui.message(LoggedIn,"Update","Weight updated successfuly.")
        else:
            Ui.message(LoggedIn,"Error","Error, please input numbers in weight field.")
        if age != "" and age.isdigit():
            user_dbmg.update_age(int(age), self.userName)
            Ui.message(LoggedIn,"Update","Age updated successfuly.")
        else:
            Ui.message(LoggedIn,"Update","Error, please input numbers in age field.")
        if target != "":
            user_dbmg.update_target(target, self.userName)
            Ui.message(LoggedIn,"Update","Target updated successfuly.")
        self.your_day_data(self.new_user)
        user_dbmg.conn.close()

    def find_meal(self):
        self.searchChoicesMeal.clear()
        products = [self.searchList.item(x).text() for x in range(self.searchList.count())]
        finddbmg = DatabaseManger('dbmeal.db')
        results = finddbmg.find_meals(products)
        for result in results:
            self.searchChoicesMeal.addItem(str(result[0]))
        finddbmg.conn.close()
        
    def find_last_index(self):
        newdbmg = DatabaseManger('dbmeal.db')
        current_index = newdbmg.query("SELECT quantity_id FROM quantity")

    def combo_on_box_changed(self, value):
        number = 4
        meals_dbmg = DatabaseManger("dbmeal.db")
        results = meals_dbmg.find_meal_by_meal_name(value)
        ingredients = []
        quantity_list = []
        recipe_descr = None
        prep_time = None
        for id, desc in enumerate(results):
            for type,value in enumerate(desc):
                if type == 8:
                    prep_time = value
                if type == 1:
                    ingredients.append(value)
                if type == 3:
                    quantity_list.append(str(value))        
                if type == 2:
                    recipe_descr = value
        
        meals_dbmg.conn.close()

        def add_values(number):
            """Returning sum of choosen type number(used to count carbs, proteins, fats and kcal)"""
            total_value = 0
            quantity = 0
            value_times_quantity = 0
            for id, desc in enumerate(results):
                    for type,value in enumerate(desc):                            
                            if type == number:
                                value_times_quantity = value * quantity / 100
                                total_value += value_times_quantity                    
                            if type == 3:
                                quantity = value
            return round(total_value,2)

        self.searchProducts.setRowCount(0)
        for row, item in enumerate(ingredients):
            self.searchProducts.insertRow(row)
            for i in range(0,len(ingredients)):
                cell_info = QtWidgets.QTableWidgetItem(str(item))
                cell_info.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.searchProducts.setItem(row, 0, cell_info )
        for row, item in enumerate(quantity_list):
            for i in range(0,len(quantity_list)):
                cell_info = QtWidgets.QTableWidgetItem(str(item))
                cell_info.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.searchProducts.setItem(row, 1, cell_info)

        self.searchReceipe.setPlainText("Receipe: {}".format(recipe_descr))
        self.searchKcal.setText("Kcal: {}".format(add_values(7)))
        self.searchProteinsCarbsFats.setText("Proteins: {}, Carbs: {}, Fats: {}".format(add_values(5),add_values(4),add_values(6)))
        self.searchPrepareTime.setText("Prepare time: {}".format(prep_time))
        
    def add_products_to_search(self):
        dbmg1 = DatabaseManger('dbmeal.db')
        ingredients = dbmg1.get_all_ingredients()
        for ingredient in ingredients:
            self.searchNewProduct.addItems(ingredient) 
        dbmg1.conn.close()

    def delete_button(self):
        self.searchList.takeItem(self.searchList.currentRow())

    def find_meal_addBtn(self):
        products = [self.searchList.item(x).text() for x in range(self.searchList.count())]
        new_product = self.searchNewProduct.currentText()
        if new_product in products:
            Ui.message(LoggedIn,"Error", "That ingredient is already on your list.")
        else:
            self.searchList.addItem(new_product)
        QtCore.QCoreApplication.processEvents()

    def select_meal_for_info(self):
        self.selected_meal = self.mealsList.currentItem().text()
        self.meal_detail = MealDetails(self.selected_meal)
        self.meal_detail.show()
        return self.selected_meal, self.meal_detail

    def selected_day(self):
        self.selected_day = self.choosenDay.currentText()
        self.day_detail = DayDetail(self.selected_day,self.userName)
        self.day_detail.show()
        return self.selected_day, self.day_detail

    def get_meal_for_day(self,day,meal_number):
        dbmg1 = DatabaseManger('dbmeal.db')
        meal = dbmg1.get_meals_for_choosen_day(day,meal_number)
        calories = 0
        proteins = 0
        carbs = 0
        fats = 0
        try:
            for kcal in meal:
                calories += kcal[6]
            for protein in meal:
                proteins += protein[7]
            for carb in meal:
                carbs += carb[8]
            for fat in meal:
                fats += carb[9]
            meal = Meal(meal[0][0],None,None,None,None,None,None,None,calories,proteins,carbs,fats)
            return meal
        except Exception as e:
            print(e)

    def update_meals_in_user_day_on_load(self):
        self.mondayMealOne.setText(self.get_meal_for_day('Monday',1).name)
        self.mondayMealTwo.setText(self.get_meal_for_day('Monday',2).name)
        self.mondayMealThree.setText(self.get_meal_for_day('Monday',3).name)
        self.mondayMealFour.setText(self.get_meal_for_day('Monday',4).name)
        self.mondayMealFive.setText(self.get_meal_for_day('Monday',5).name)
        self.mondayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Monday',1).calories+self.get_meal_for_day('Monday',2).calories+
                                self.get_meal_for_day('Monday',3).calories+self.get_meal_for_day('Monday',4).calories+self.get_meal_for_day('Monday',5).calories)))

        self.tuesdayMealOne.setText(self.get_meal_for_day('Tuesday',1).name)
        self.tuesdayMealTwo.setText(self.get_meal_for_day('Tuesday',2).name)
        self.tuesdayMealThree.setText(self.get_meal_for_day('Tuesday',3).name)
        self.tuesdayMealFour.setText(self.get_meal_for_day('Tuesday',4).name)
        self.tuesdayMealFive.setText(self.get_meal_for_day('Tuesday',5).name)
        self.tuesdayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Tuesday',1).calories+self.get_meal_for_day('Tuesday',2).calories+
                                self.get_meal_for_day('Tuesday',3).calories+self.get_meal_for_day('Tuesday',4).calories+self.get_meal_for_day('Tuesday',5).calories)))

        self.wednesdayMealOne.setText(self.get_meal_for_day('Wednesday',1).name)
        self.wednesdayMealTwo.setText(self.get_meal_for_day('Wednesday',2).name)
        self.wednesdayMealThree.setText(self.get_meal_for_day('Wednesday',3).name)
        self.wednesdayMealFour.setText(self.get_meal_for_day('Wednesday',4).name)
        self.wednesdayMealFive.setText(self.get_meal_for_day('Wednesday',5).name)
        self.wednesdayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Wednesday',1).calories+self.get_meal_for_day('Wednesday',2).calories+
                                self.get_meal_for_day('Wednesday',3).calories+self.get_meal_for_day('Wednesday',4).calories+self.get_meal_for_day('Wednesday',5).calories)))


        self.thursdayMealOne.setText(self.get_meal_for_day('Thursday',1).name)
        self.thursdayMealTwo.setText(self.get_meal_for_day('Thursday',2).name)
        self.thursdayMealThree.setText(self.get_meal_for_day('Thursday',3).name)
        self.thursdayMealFour.setText(self.get_meal_for_day('Thursday',4).name)
        self.thursdayMealFive.setText(self.get_meal_for_day('Thursday',5).name)
        self.thursdayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Thursday',1).calories+self.get_meal_for_day('Thursday',2).calories+
                                self.get_meal_for_day('Thursday',3).calories+self.get_meal_for_day('Thursday',4).calories+self.get_meal_for_day('Thursday',5).calories)))


        self.fridayMealOne.setText(self.get_meal_for_day('Friday',1).name)
        self.fridayMealTwo.setText(self.get_meal_for_day('Friday',2).name)
        self.fridayMealThree.setText(self.get_meal_for_day('Friday',3).name)
        self.fridayMealFour.setText(self.get_meal_for_day('Friday',4).name)
        self.fridayMealFive.setText(self.get_meal_for_day('Friday',5).name)
        self.fridayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Friday',1).calories+self.get_meal_for_day('Friday',2).calories+
                                self.get_meal_for_day('Friday',3).calories+self.get_meal_for_day('Friday',4).calories+self.get_meal_for_day('Friday',5).calories)))

        self.saturdayMealOne.setText(self.get_meal_for_day('Saturday',1).name)
        self.saturdayMealTwo.setText(self.get_meal_for_day('Saturday',2).name)
        self.saturdayMealThree.setText(self.get_meal_for_day('Saturday',3).name)
        self.saturdayMealFour.setText(self.get_meal_for_day('Saturday',4).name)
        self.saturdayMealFive.setText(self.get_meal_for_day('Saturday',5).name)
        self.saturdayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Saturday',1).calories+self.get_meal_for_day('Saturday',2).calories+
                                self.get_meal_for_day('Saturday',3).calories+self.get_meal_for_day('Saturday',4).calories+self.get_meal_for_day('Saturday',5).calories)))

        self.sundayMealOne.setText(self.get_meal_for_day('Sunday',1).name)
        self.sundayMealTwo.setText(self.get_meal_for_day('Sunday',2).name)
        self.sundayMealThree.setText(self.get_meal_for_day('Sunday',3).name)
        self.sundayMealFour.setText(self.get_meal_for_day('Sunday',4).name)
        self.sundayMealFive.setText(self.get_meal_for_day('Sunday',5).name)
        self.sundayTotal.setText('Total calories: {}'.format(str(self.get_meal_for_day('Sunday',1).calories+self.get_meal_for_day('Sunday',2).calories+
                                self.get_meal_for_day('Sunday',3).calories+self.get_meal_for_day('Sunday',4).calories+self.get_meal_for_day('Sunday',5).calories)))


class MealDetails(QtWidgets.QWidget):
    def __init__(self, selected_meal):
        super(MealDetails, self).__init__()
        uic.loadUi('meal_details.ui',self)
        self.meal = selected_meal
        self.show_meal_details()
        self.setStyleSheet(qdarkgraystyle.load_stylesheet())
    def show_meal_details(self):
        nowydb = DatabaseManger('dbmeal.db')
        meals = nowydb.get_meal_detail_by_name(self.meal)
        
        ingredient_list = []
        quantity_list = []
        kcal = 0; proteins = 0; carbohydrates = 0; fats = 0

        for meal in meals:
            ingredient = meal[1]
            ingredient_list.append(ingredient)
            quantity = meal[2]
            quantity_list.append(quantity)
        
        for meal in range(len(meals)):
            kcal += meals[meal][8]*meals[meal][2]/100
            proteins += meals[meal][4]*meals[meal][2]/100
            carbohydrates += meals[meal][5]*meals[meal][2]/100
            fats += meals[meal][6]*meals[meal][2]/100

        meal_class = Meal(meals[0][0],ingredient_list,quantity_list,meals[0][3],meals[0][7],meals[0][9],None,None,kcal,proteins,carbohydrates,fats)
        self.meal_name = self.findChild(QtWidgets.QLabel, 'meal_name')
        self.meal_name.setText(meal_class.name.capitalize())
        self.prep_time = self.findChild(QtWidgets.QLabel, 'prep_time')
        self.prep_time.setText("Time to prepare food: {}".format(meal_class.prep_time))
        self.proteins = self.findChild(QtWidgets.QLabel, 'proteins')
        self.proteins.setText("Proteins: {}".format(round(proteins, 1)))
        self.carbohydrates = self.findChild(QtWidgets.QLabel, 'carbohydrates')
        self.carbohydrates.setText("Carbohydrates: {}".format(round(carbohydrates, 1)))
        self.fats = self.findChild(QtWidgets.QLabel, 'fats')
        self.fats.setText("Fats: {}".format(round(fats, 1)))
        self.calories = self.findChild(QtWidgets.QLabel, 'calories')
        self.calories.setText("Calories: {}".format(kcal))
        self.recipe = self.findChild(QtWidgets.QTextEdit, 'recipe')
        self.recipe.setPlainText("Recipe: \n\n {}".format(meals[0][3]))
        self.ingredientTable = self.findChild(QtWidgets.QTableWidget, 'ingredientTable')
        self.ingredientTable.setRowCount(0)

        for row, item in enumerate(ingredient_list):
            self.ingredientTable.insertRow(row)
            for i in range(0,len(ingredient_list)):
                cell_info = QtWidgets.QTableWidgetItem(str(item))
                cell_info.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ingredientTable.setItem(row, 0, cell_info )
        for row, item in enumerate(quantity_list):
            for i in range(0,len(quantity_list)):
                cell_info = QtWidgets.QTableWidgetItem(str(item))
                cell_info.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ingredientTable.setItem(row, 1, cell_info)
        nowydb.conn.close()

class DayDetail(QtWidgets.QMainWindow):
    def __init__(self, selected_day,user):
        super(DayDetail, self).__init__()
        uic.loadUi('day_details.ui',self)
        self.day = selected_day
        self.user = user
        self.get_meal_list()
        self.setStyleSheet(qdarkgraystyle.load_stylesheet())
        self.dayDay = self.findChild(QtWidgets.QLabel, 'dayDay')
        self.meal1Name = self.findChild(QtWidgets.QLabel, 'meal1Name')
        self.comboMeal1 = self.findChild(QtWidgets.QComboBox, 'comboMeal1')
        self.meal2Name = self.findChild(QtWidgets.QLabel, 'meal2Name')
        self.comboMeal2 = self.findChild(QtWidgets.QComboBox, 'comboMeal2')
        self.meal3Name = self.findChild(QtWidgets.QLabel, 'meal3Name')
        self.comboMeal3 = self.findChild(QtWidgets.QComboBox, 'comboMeal3')
        self.meal4Name = self.findChild(QtWidgets.QLabel, 'meal4Name')
        self.comboMeal4 = self.findChild(QtWidgets.QComboBox, 'comboMeal4')
        self.meal5Name = self.findChild(QtWidgets.QLabel, 'meal5Name')
        self.comboMeal5 = self.findChild(QtWidgets.QComboBox, 'comboMeal5')
        self.saveBtn = self.findChild(QtWidgets.QPushButton, 'saveBtn')
        self.saveBtn.clicked.connect(self.save_day)
        self.mealQuantityEdit = self.findChild(QtWidgets.QComboBox, 'mealQuantityEdit')
        self.mealEditButton = self.findChild(QtWidgets.QPushButton, 'mealEditButton')
        self.dayDay.setText(str(self.day))
        
    def get_meal_list(self):
        all_meals = dbmg.get_all_meals()
        for meal in all_meals:
            self.comboMeal1.addItem(meal['name'])
            self.comboMeal2.addItem(meal['name'])
            self.comboMeal3.addItem(meal['name'])
            self.comboMeal4.addItem(meal['name'])
            self.comboMeal5.addItem(meal['name'])
        
    def save_day(self):
        dbmg = DatabaseManger('dbmeal.db')
        dbmg.save_user_day(self.comboMeal1.currentText(),self.day,self.user,1)
        dbmg.save_user_day(self.comboMeal2.currentText(),self.day,self.user,2)
        dbmg.save_user_day(self.comboMeal3.currentText(),self.day,self.user,3)
        dbmg.save_user_day(self.comboMeal4.currentText(),self.day,self.user,4)
        dbmg.save_user_day(self.comboMeal5.currentText(),self.day,self.user,5)
        window.loggedUser.update_meals_in_user_day_on_load()

dbmg = DatabaseManger("dbmeal.db")
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()