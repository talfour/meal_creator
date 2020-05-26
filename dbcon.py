import sqlite3
import re
import random
from itertools import permutations



class DatabaseManger(object):
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()
        
    def query_extra(self, arg, args):
        """Pass an query in argument with extra kwargs"""
        self.cur.execute(arg, args)
        self.conn.commit()
        return self.cur

    def query(self, arg):
        """Pass an query in argument"""
        self.cur.execute(arg)
        self.conn.commit()
        return self.cur

    def set_random_recipe_id(self,row_start,row_finish):
        for i in range(row_start,row_finish):
            random_meal = random.choice(self.get_all_meals_to_randomize())
            meal = random_meal['name']
            self.cur.execute("UPDATE User_Week SET recipe_id = ? WHERE user_week_id = ? AND user_id = (SELECT user_id FROM Users ORDER BY user_id DESC LIMIT 1)",(meal,i,))
            self.conn.commit()

    def set_meal_id(self,row_start,row_finish):
        """Set meal_id for new user. We got 5 meals each day."""
        meal_id = 1
        for i in range(row_start, row_finish):
            self.cur.execute("UPDATE User_Week SET meal_id = ? WHERE user_week_id = ? AND user_id = (SELECT user_id FROM Users ORDER BY user_id DESC LIMIT 1)",(meal_id,i,))
            self.conn.commit()
            meal_id += 1

    def set_day(self,row_start,row_finish,day_id):
        """Set day_id for new user"""
        for i in range(row_start,row_finish):
            self.cur.execute("UPDATE User_Week SET day_id = ? WHERE user_id = (SELECT user_id FROM Users ORDER BY user_id DESC LIMIT 1) AND user_week_id = ?",(day_id,i,))
            self.conn.commit()     

    def prepare_week_for_new_user(self):
        """After creating new user prepare table for him."""
        for i in range(35):
            self.cur.execute("INSERT INTO User_Week VALUES (Null, Null, (SELECT user_id FROM Users ORDER BY user_id DESC LIMIT 1),Null, Null)")
            self.conn.commit()


    def add_user_todb(self, name, weight, height, age, gender, target):   
        self.query_extra("INSERT INTO Users VALUES (Null,:name, :weight, :height, :age, :gender, :target)",
                                                {'name': name, 'weight': weight, 'height': height,'age': age, 'gender': gender, 'target': target })

    def create_user_and_his_week(self,name,weight,height,age,gender,target):
        self.add_user_todb(name, weight, height, age, gender, target)
        self.prepare_week_for_new_user()
        #after create an user and insert new records for him need to get his all unique id's and last id
        self.cur.execute("SELECT user_week_id from User_Week WHERE user_id = (SELECT user_id FROM Users ORDER BY user_id DESC LIMIT 1)")
        all_rows = self.cur.fetchall()
        print(all_rows[0]['name'])
        self.cur.execute("SELECT user_week_id from User_Week WHERE user_id = (SELECT user_id FROM Users ORDER BY user_id DESC LIMIT 1) ORDER BY user_week_id DESC LIMIT 1")
        last_row = self.cur.fetchall()
        print(last_row[0]['name'])
        #update days
        self.set_day(all_rows[0]['name'],last_row[0]['name']-29,1) 
        self.set_day(all_rows[0]['name']+5,last_row[0]['name']-24,2) 
        self.set_day(all_rows[0]['name']+10,last_row[0]['name']-19,3)
        self.set_day(all_rows[0]['name']+15,last_row[0]['name']-14,4)
        self.set_day(all_rows[0]['name']+20,last_row[0]['name']-9,5)
        self.set_day(all_rows[0]['name']+25,last_row[0]['name']-4,6)
        self.set_day(all_rows[0]['name']+30,last_row[0]['name']+1,7)
        #update meal_id's
        self.set_meal_id(all_rows[0]['name'],last_row[0]['name']-29)
        self.set_meal_id(all_rows[0]['name']+5,last_row[0]['name']-24)
        self.set_meal_id(all_rows[0]['name']+10,last_row[0]['name']-19)
        self.set_meal_id(all_rows[0]['name']+15,last_row[0]['name']-14)
        self.set_meal_id(all_rows[0]['name']+20,last_row[0]['name']-9)
        self.set_meal_id(all_rows[0]['name']+25,last_row[0]['name']-4)
        self.set_meal_id(all_rows[0]['name']+30,last_row[0]['name']+1)
        #insert a random meals at the begining to prevent user reciving an error while filling meal list in user day tab.
        self.set_random_recipe_id(all_rows[0]['name'],last_row[0]['name']+1)

    def update_target(self, target, name):
        self.query_extra("""UPDATE users SET target = :target
                        WHERE name = :name""",{'name':name, 'target':target})
    
    def update_weight(self, weight, name):
        self.query_extra("""UPDATE users SET weight = :weight
                        WHERE name = :name""",{'name':name, 'weight':weight})

    def update_age(self, age, name):
        self.query_extra("""UPDATE users SET age = :age
                        WHERE name = :name""",{'name':name, 'age':age})

    def get_user_byname(self, name):
        self.query_extra("SELECT * FROM users WHERE name=:name""", {'name':name})
        return self.cur.fetchall()

    def get_all_users(self):
        self.cur.row_factory = lambda cursor, row: {'name':row[0]}
        self.query("SELECT name FROM users")    
        return self.cur.fetchall()

    def get_all_products(self):
        self.query("SELECT * FROM Ingredients ORDER BY ingredient_name ASC")
        return self.cur.fetchall()

    def get_all_meals_to_randomize(self):
        self.query("SELECT recipe_id FROM Recipe")
        return self.cur.fetchall()

    def get_all_meals(self):
        self.query("SELECT recipe_name FROM Recipe ORDER BY recipe_name ASC")
        return self.cur.fetchall()

    def get_meal_detail_by_name(self,meal_name):
        self.query_extra("""SELECT 
                                r.recipe_name,
                                i.ingredient_name,
                                q.ingredient_quantity,
                                r.recipe_description,
                                i.ingredient_proteins,
                                i.ingredient_carbohydrates,
                                i.ingredient_fats,
                                r.prep_time,
                                i.ingredient_calories,
                                r.last_time_used
                                FROM Recipe as r
                                JOIN Quantity as q ON q.ingredient_id = i.ingredient_id
                                JOIN Ingredients as i ON r.recipe_id = q.recipe_id
                                WHERE recipe_name = (?)""",(meal_name,))
        return self.cur.fetchall()

    def get_food_categories(self):
        self.query("SELECT DISTINCT ingredient_category from Ingredients ORDER BY ingredient_category ASC")
        return self.cur.fetchall()

    def get_meal_by_id(self,random_id):
        self.query_extra("""SELECT
                                r.recipe_name,
                                r.prep_time,
                                r.last_time_used,
                                i.ingredient_fats,
                                i.ingredient_name,
                                i.ingredient_proteins,
                                i.ingredient_id,
                                i.ingredient_carbohydrates,
                                q.quantity_id,
                                q.ingredient_quantity,
                                r.recipe_description,
                                i.ingredient_calories
                                FROM Recipe as r
                                JOIN Ingredients as i ON i.ingredient_id = q.ingredient_id
                                JOIN Quantity as q ON q.recipe_id = r.recipe_id
                                WHERE r.recipe_id = (?)""",(random_id,))
        return self.cur.fetchall()


    def add_meal(self, recipe_name,zipped, ingredient_list,quantity_list, recipe_description, prep_time):
        
        self.query_extra("INSERT INTO Recipe (recipe_name, prep_time, recipe_description) VALUES (:recipe_name, :prep_time, :recipe_description)",
                            {'recipe_name':recipe_name, 'prep_time':prep_time, 'recipe_description':recipe_description})

        for item in ingredient_list:
            self.query_extra("INSERT INTO Quantity (recipe_id) VALUES ((SELECT recipe_id from Recipe WHERE recipe_name=:recipe_name))",
                            {'recipe_name':recipe_name})
        
        self.cur.executemany('UPDATE Quantity SET ingredient_id = (SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?), ingredient_quantity = ? WHERE quantity_id = ?',(zipped))
        self.conn.commit()
       
    def check_last_id(self):
        self.query("SELECT quantity_id FROM Quantity ORDER BY quantity_id DESC LIMIT 1")
        return self.cur.fetchall()

    def add_product(self, ingredient_name, ingredient_category, ingredient_calories, ingredient_protein, ingredient_carbohydrates, ingredient_fat):
        self.query_extra("INSERT INTO ingredients VALUES (null, :ingredient_name, :ingredient_category, :ingredient_calories, :ingredient_protein, :ingredient_carbohydrates, :ingredient_fat)",
                                                {'ingredient_name': ingredient_name, 'ingredient_category': ingredient_category, 'ingredient_calories': ingredient_calories,'ingredient_protein': ingredient_protein,
                                                 'ingredient_carbohydrates': ingredient_carbohydrates, 'ingredient_fat': ingredient_fat })

    def delete_product(self, ingredient_id):
        self.query_extra("DELETE FROM ingredients WHERE ingredient_id=:ingredient_id",{'ingredient_id':ingredient_id})

    def update_date(self, recipe_id, last_time_used):
        self.query_extra("""UPDATE recipe SET last_time_used = :last_time_used WHERE recipe_id=:recipe_id""",{'recipe_id':recipe_id, 'last_time_used':last_time_used })


    def find_meals(self,words):
        combinations = ["%" + "%".join(order) + "%" for order in list(permutations(words))]
        sql_1 = """SELECT
                        r.recipe_name,
                        r.prep_time,
                        r.last_time_used,
                        i.ingredient_fats,
                        i.ingredient_name,
                        i.ingredient_proteins,
                        i.ingredient_id,
                        i.ingredient_carbohydrates,
                        q.quantity_id,
                        q.ingredient_quantity,
                        r.recipe_description,
                        i.ingredient_calories
                        FROM Ingredients as i
                        JOIN Quantity as q ON q.ingredient_id = i.ingredient_id
                        JOIN Recipe as r ON r.recipe_id = q.recipe_id
                        WHERE i.ingredient_name LIKE {0}""".format(" OR i.ingredient_name LIKE".join('(?)' for _ in combinations))
                
        values = combinations
        self.query_extra(sql_1, values)        
        return self.cur.fetchall()

    def find_meal_by_meal_name(self,recipe_name):
        self.query_extra("""SELECT 
                                r.recipe_name,
                                i.ingredient_name,
                                r.recipe_description,
                                q.ingredient_quantity,
                                i.ingredient_carbohydrates,
                                i.ingredient_proteins,
                                i.ingredient_fats,
                                i.ingredient_calories,
                                r.prep_time
                                FROM recipe as r 
                                JOIN Ingredients as i ON i.ingredient_id = q.ingredient_id
                                JOIN Quantity as q ON q.recipe_id = r.recipe_id
                                WHERE recipe_name LIKE (:recipe_name)""",{'recipe_name':recipe_name})
        
        return self.cur.fetchall() 

    def get_all_ingredients(self):
        self.query("SELECT ingredient_name FROM Ingredients")
        return self.cur.fetchall()        

    def get_day_details(self,user_name,day):
        self.query_extra("""SELECT 
                                r.recipe_id,
                                d.day_name,
                                mfu.user_id,
                                r.recipe_name,
                                i.ingredient_calories,
                                i.ingredient_proteins,
                                i.ingredient_carbohydrates,
                                i.ingredient_fats,
                                q.ingredient_quantity
                                FROM Meal_For_User as mfu
                                JOIN User_Week as uw ON mfu.meal_for_user_id = uw.meal_for_user_id
                                JOIN Days as d ON d.day_id = uw.day_id
                                JOIN Recipe as r ON mfu.recipe_id = r.recipe_id
                                JOIN Quantity as q ON q.recipe_id = r.recipe_id
                                JOIN Ingredients as i ON i.ingredient_id = q.ingredient_id
                                JOIN Users as u ON u.user_id = mfu.user_id
                                WHERE u.name = :user_name AND d.day_name = :day""",{'user_name':user_name, 'day':day})
    
    def get_id_for_day(self,day_name):
        self.query_extra("""SELECT day_id FROM Days WHERE day_name = ?""",(day_name,))
        return self.cur.fetchall()

    def get_id_for_recipe(self,recipe):
        self.query_extra("""SELECT recipe_id FROM Recipe WHERE recipe_name = ?""",(recipe,))
        return self.cur.fetchall()

    def save_user_day(self,recipe_id,day_name,user_name,meal_id):
        self.query_extra("""UPDATE User_Week SET recipe_id = (SELECT recipe_id FROM Recipe WHERE recipe_name = ?)
                                WHERE day_id = (SELECT day_id FROM Days WHERE day_name = ?) 
                                AND user_id = (SELECT user_id FROM Users WHERE name = ?)
                                AND meal_id = ?""",(recipe_id,day_name,user_name,meal_id))
        
    def get_meals_for_choosen_day(self,day,meal_number):
        self.query_extra("""SELECT 
                                r.recipe_name,
                                uw.user_id,
                                uw.day_id,
                                uw.meal_id,
                                uw.recipe_id,
                                q.ingredient_quantity,
                                i.ingredient_calories,
                                i.ingredient_proteins,
                                i.ingredient_carbohydrates,
                                i.ingredient_fats,
                                i.ingredient_name
                                FROM User_Week as uw
                                JOIN Recipe as r ON uw.recipe_id = r.recipe_id
                                JOIN Quantity as q ON q.recipe_id = r.recipe_id
                                JOIN Ingredients as i ON i.ingredient_id = q.ingredient_id
                                JOIN Days as d ON uw.day_id = d.day_id
                                WHERE uw.day_id = (SELECT d.day_id WHERE d.day_name = ?) AND uw.meal_id = ?
                                ORDER BY meal_id ASC""",(day,meal_number))
        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.conn.close()