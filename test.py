import unittest
from dbcon import DatabaseManger
from ingredient import Ingredient
from meals import Meal
from user import User


class Test(unittest.TestCase):

    def test_user_kcal(self):
        """Test to check user kcal"""
        user = User('Kuba',85,183,25,'Male','reduction')
        kcal = user.calories
        self.assertAlmostEqual(kcal, 2672.99)


    def test_BMR(self):
        user = User('Kuba',85,183,25,'Male','reduction')
        bmr = user.BMR
        self.assertEqual(bmr, 2520.9)
    

if __name__ == '__main__':
    unittest.main()