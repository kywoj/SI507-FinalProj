from food import *
import unittest


## DATA ACCESS TEST
class TestAccess(unittest.TestCase):
	def test_requests(self):
		food = 'carrots'
		item_ndbnum = '45015213'

		results_1 = request_food_ndbnum(food)
		almost_usable_results_1 = json.loads(results_1)
		usable_results_1 = almost_usable_results_1["list"]["item"]

		results_2 = request_food_info(item_ndbnum)
		almost_usable_results_2 = json.loads(results_2)
		usable_results_2 = almost_usable_results_2["report"]["food"]
		
		self.assertEqual(usable_results_1[0]["group"], 'Branded Food Products Database')
		self.assertEqual(usable_results_1[7]["ndbno"], '45015213')
		self.assertNotEqual(usable_results_1[8]["ndbno"], '45015213')
		self.assertEqual(usable_results_1[16]["name"], 'BABY CARROT WITH WHITE CHEDDAR CHEESE & ALMONDS, UPC: 649632001452')
		self.assertNotEqual(usable_results_1[17]["name"], 'BABY CARROT WITH WHITE CHEDDAR CHEESE & ALMONDS, UPC: 649632001452')
		self.assertEqual(usable_results_2["name"], "ANTONINA'S ARTISAN BAKERY, MINI PANCAKES, CARROT, UPC: 898223002914")
		self.assertEqual(usable_results_2["ds"], 'Label Insight')
		self.assertNotEqual(usable_results_2["ru"], 'ml')


## DATA STORAGE TEST
class TestStorage(unittest.TestCase):

	def test_tables(self):
		conn = sqlite3.connect('food.db')
		cur = conn.cursor()
		populate_tables("apples")

		sql = 'SELECT Calories FROM NutritionalInfo'
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertIn(('320',), result_list)
		self.assertNotIn(('1000',), result_list)
		self.assertEqual(111, len(result_list))

		sql = 'SELECT Ndb FROM NdbNums'
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertIn(('45182028',), result_list)
		self.assertNotIn(('45187081',), result_list)
		self.assertEqual(200, len(result_list))


## DATA PROCESSING TEST
class TestProcessing(unittest.TestCase):
	
	def test_classes(self):
			daily_dict1 = {'Baby carrots': ('35', '85.0', 'g', '1.00', '0.00', '8.00'), 'Alpina, vanilla low fat yogurt, chocolate pretzel': ('130', '113.0', 'g', '4.00', '2.99', '20.00'), 'Boneless chicken breast': ('169', '140.0', 'g', '25.00', '3.00', '13.01'), 'Honeycrisp apple': ('5', '236.5', 'ml', '0.00', '0.00', '9.01')}
			cal_goal = '1200'
			results_list1 = presentable_data(daily_dict1, cal_goal)

			self.assertEqual(results_list1[2].name, 'Boneless chicken breast')
			self.assertEqual(results_list1[1].protein, '4.00')
			self.assertNotEqual(results_list1[0].protein, '4.00')

			daily_dict2 = {"Mcdonald's, big mac": ('563', '219.0', 'g', '25.89', '32.76', '43.98'), 'Cheetos, crunchy cheese flavored snacks, cheddar jalapeno': ('160', '28.0', 'g', '2.00', '10.00', '13.00'), 'Celery & carrot with lite ranch dip': ('90', '113.0', 'g', '0.99', '6.99', '6.99')}
			results_list2 = presentable_data(daily_dict2, cal_goal)

			self.assertEqual(results_list2[2].name, 'Celery & carrot with lite ranch dip')
			self.assertEqual(results_list2[1].protein, '2.00')
			self.assertNotEqual(results_list2[0].protein, '2.00')


unittest.main()