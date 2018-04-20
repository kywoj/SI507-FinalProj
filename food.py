import sqlite3
import csv
import json
import requests
import plotly.plotly as py
import plotly.graph_objs as go
import pytumblr
import datetime
import usda_secrets
import tumblr_secrets
import sys

## PRIVATE KEYS
usda_key = usda_secrets.usda_key
client = pytumblr.TumblrRestClient(tumblr_secrets.consumer_key, tumblr_secrets.consumer_secret, tumblr_secrets.oauth_token, tumblr_secrets.oauth_secret)

##########

## GLOBAL VARIABLE
today = datetime.date.today().strftime("%B %d, %Y")

##########

## CACHING FILES
NDBNUM_CACHE_FNAME = 'ndbnum_cache.json'

INFO_CACHE_FNAME = 'info_cache.json'

try:
    ndbnum_cache_file = open(NDBNUM_CACHE_FNAME, 'r')
    ndbnum_cache_contents = ndbnum_cache_file.read()
    NDBNUM_CACHE_DICTION = json.loads(ndbnum_cache_contents)
    ndbnum_cache_file.close()
except:
    NDBNUM_CACHE_DICTION = {}

try:
    info_cache_file = open(INFO_CACHE_FNAME, 'r')
    info_cache_contents = info_cache_file.read()
    INFO_CACHE_DICTION = json.loads(info_cache_contents)
    info_cache_file.close()
except:
    INFO_CACHE_DICTION = {}

##########

## CACHING FUNCTION 1
def request_food_ndbnum(food):
	if food in NDBNUM_CACHE_DICTION:
		#print("Getting cached data...")
		return NDBNUM_CACHE_DICTION[food]
	else:
		#print("Making a request for new data...")
		ndbnum = requests.get("https://api.nal.usda.gov/ndb/search/?format=json&q={}&sort=n&max=200&offset=0&api_key={}".format(food, usda_key)) 
		NDBNUM_CACHE_DICTION[food] = ndbnum.text
		dumped_json_cache = json.dumps(NDBNUM_CACHE_DICTION)
		fw = open(NDBNUM_CACHE_FNAME,"w")
		fw.write(dumped_json_cache)
		fw.close()
		return NDBNUM_CACHE_DICTION[food]

##########

## CACHING FUNCTION2
def request_food_info(item_ndbnum):
		if item_ndbnum in INFO_CACHE_DICTION:
			#print("Getting cached data...")
			return INFO_CACHE_DICTION[item_ndbnum]
		else:
			#print("Making a request for new data...")
			item_info_req = requests.get("https://api.nal.usda.gov/ndb/reports/?ndbno={}&type=b&format=json&api_key={}".format(item_ndbnum, usda_key))
			INFO_CACHE_DICTION[item_ndbnum] = item_info_req.text
			dumped_json_cache = json.dumps(INFO_CACHE_DICTION)
			fw = open(INFO_CACHE_FNAME,"w")
			fw.write(dumped_json_cache)
			fw.close()
			return INFO_CACHE_DICTION[item_ndbnum]

##########

## DATABASE & TABLE CREATION 
conn = sqlite3.connect('food.db')
cur = conn.cursor()

ndbnums_statement = '''
DROP TABLE IF EXISTS 'NdbNums';
'''
cur.execute(ndbnums_statement)


ndbnums_table = '''
CREATE TABLE 'NdbNums' (
	'Ndb' TEXT NOT NULL,
    'FoodName' TEXT NOT NULL,
    'Upc' TEXT NOT NULL,
    'Gp' TEXT NOT NULL,
    'DS' TEXT NOT NULL,
    PRIMARY KEY('Ndb')
);

'''
cur.execute(ndbnums_table)


nut_statement = '''
DROP TABLE IF EXISTS 'NutritionalInfo';
'''
cur.execute(nut_statement)


nut_table = '''
CREATE TABLE 'NutritionalInfo' (
    'Id' INTEGER NOT NULL,
    'FoodName' TEXT NOT NULL,
    'FoodNdb' TEXT,
    'Calories' TEXT NOT NULL,
    'ServSize' TEXT NOT NULL,
    'ServMeasure' TEXT NOT NULL,
    'ServLabel' TEXT NOT NULL,
    'Protein' TEXT NOT NULL,
    'Fat' TEXT NOT NULL,
    'Carbs' TEXT NOT NULL,
    PRIMARY KEY('Id')
    FOREIGN KEY ('FoodNdb') REFERENCES NdbNums('Ndb')

);

'''
cur.execute(nut_table)


conn.commit()

##########


## POPULATE TABLES
def populate_tables(food):

	# DELETE ANY EXISTING DATA IN TABLES
	delete_statement_ndb = '''
	DELETE FROM 'NutritionalInfo';
	'''
	delete_statement_nut = '''
	DELETE FROM 'NdbNums';
	'''
	cur.execute(delete_statement_ndb)
	cur.execute(delete_statement_nut)
	conn.commit()

	# SEARCH FOR FOOD
	ndbnum_info = request_food_ndbnum(food)
	usable_ndbnum_info = json.loads(ndbnum_info)
	usable_ndbnum_info_list = usable_ndbnum_info["list"]["item"]

	#ADD FOOD SEARCH RESULTS INTO NdbNums TABLE
	ind_item_ndbnum_info_dict = {}
	for item in usable_ndbnum_info_list:
		item_name_upc = item["name"].capitalize().split("upc: ")
		if len(item_name_upc) == 2:
			item_name = item_name_upc[0].rstrip(", ")
			item_upc = item_name_upc[1]
		else:
			item_name = item_name_upc[0]
			item_upc = "NO UPC"
		item_ndbnum_list = item["ndbno"]
		item_group = item["group"]
		item_ds = item["ds"]
		
		item_ndbnum_info_name = [item_ndbnum_list, item_name, item_upc, item_group, item_ds]
		item_ndbnum_info = [item_upc, item_ndbnum_list, item_group, item_ds]
	
		ind_item_ndbnum_info_dict[item_name] = item_ndbnum_info

		cur.execute("INSERT INTO NdbNums (Ndb, FoodName, Upc, Gp, DS) VALUES (?, ?, ?, ?, ?)", item_ndbnum_info_name)
		conn.commit()

	#GET NUTRITIONAL INFO FOR FOOD & ADD INTO NutritionalInfo TABLE
	for item in ind_item_ndbnum_info_dict:
		item_ndbnum_for_dict = ind_item_ndbnum_info_dict[item][1]
		item_nutrition_info = json.loads(request_food_info(item_ndbnum_for_dict))
		
		base_item_name = item_nutrition_info["report"]["food"]["name"]
		usable_item_ndbnum = item_nutrition_info["report"]["food"]["ndbno"]
		inter_item_name = base_item_name.capitalize().split("upc: ")
		if len(inter_item_name) == 2:
			usable_item_name = inter_item_name[0].strip(", ")
			usable_item_upc = inter_item_name[1]
		else:
			usable_item_name = inter_item_name[0].strip(", ")
			usable_item_upc = "NO UPC"

		item_nutrition_info_list = []

		for part in item_nutrition_info["report"]["food"]["nutrients"]:
			if part["name"] == "Energy":
				for item in part["measures"]:
					if item == None:
						pass
					else:
						item_def_amount = item["eqv"]
						item_def_measure = item["eunit"]
						item_def_kcal = item["value"]
						item_def_label = item["label"]
						item_def_nut_info = str(item_def_kcal) + " calories per " + str(item_def_amount) + str(item_def_measure)
			if part["name"] == "Protein":
				for item in part["measures"]:
					if item == None:
						pass
					else:
						item_def_protein = item["value"]
			if part["name"] == "Total lipid (fat)":
				for item in part["measures"]:
					if item == None:
						pass
					else:
						item_def_fat = item["value"]
			if part["name"] == "Carbohydrate, by difference":
				for item in part["measures"]:
					if item == None:
						pass
					else:
						item_def_carbs = item["value"]

		item_nutrition_info_list = [usable_item_name, item_def_kcal, item_def_amount, item_def_measure, item_def_label, item_def_protein, item_def_fat, item_def_carbs]
		
		cur.execute("INSERT INTO NutritionalInfo (FoodName, Calories, ServSize, ServMeasure, ServLabel, Protein, Fat, Carbs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", item_nutrition_info_list)

		#UPDATE NutritionalInfo TABLE
		update_nut_table = '''
		UPDATE NutritionalInfo
		SET FoodNdb = 
		(
			SELECT Ndb
			FROM NdbNums
			Where NutritionalInfo.FoodName = NdbNums.FoodName
		)
		'''

		cur.execute(update_nut_table)
		conn.commit()

##########

## CLASS DEFINITION
class logEntry:
	def __init__ (self, name, cals, servsize, servmeas, protein, fat, carbs):
		self.name = name
		self.cals = cals
		self.servsize = servsize
		self.servmeas = servmeas
		self.protein = protein
		self.fat = fat
		self.carbs = carbs

	def __str__(self):
		return "{} has {} calories per {}{}, with {}g of protein, {}g of fat, and {}g of carbs".format(self.name, self.cals, self.servsize, self.servmeas, self.protein, self.fat, self.carbs)

##########

## PLOTLY FUNCTIONS
def dailyCalPlot(entryNames, entryCals):
	labels = entryNames
	values = entryCals
	colors = ['##1abc9c', '##f1c40f', '##e67e22', '##e74c3c', '###3498db', '###8e44ad']

	trace = go.Pie(labels=labels, values=values,
	               hoverinfo='label', textinfo='value', 
	               textfont=dict(size=20),
	               marker=dict(colors=colors, 
	                           line=dict(color='#000000', width=2)))
	data = [trace]
	layout = go.Layout(
	    title='Daily Calorie Log for {}'.format(today),
	)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='daily-cal-plot-{}'.format(today))

#

def dailyGoalPlot(cal_goal, dailyCals):
	trace0 = go.Bar(
	    x=["Daily Calorie Goal", "Today's Calories"],
	    y=[cal_goal, dailyCals],
	    marker=dict(
	        color=['rgba(222,45,38,0.8)', 'rgba(204,204,204,1)']),
	)

	data = [trace0]
	layout = go.Layout(
	    title='Daily Goal Log for {}'.format(today),
	)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='daily-goal-{}'.format(today))

#

def entryMacroPlot(entryNames, entryProtein, entryFat, entryCarbs):
	trace1 = go.Bar(
	    x= entryNames,
	    y= entryProtein,
	    name='Protein (grams)'
	)
	trace2 = go.Bar(
	    x= entryNames,
	    y= entryFat,
	    name='Fat (grams)'
	)
	trace3 = go.Bar(
	    x= entryNames,
	    y= entryCarbs,
	    name='Carbs (grams)'
	)

	data = [trace1, trace2, trace3]
	layout = go.Layout(
	    barmode='group',
	    title='Entry Macronutrient Log for {}'.format(today),
	)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='entry-macros-{}'.format(today))

#

def dailyMacroPlot(dailyMacros):
	data = [go.Bar(
	            x= dailyMacros,
	            y=['Protein (grams)', 'Fat (grams)', 'Carbs (grams)'],
	            orientation = 'h'
	)]
	layout = go.Layout (
		title = 'Daily Macronutrient Log for {}'.format(today)
	)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='daily-macros-{}'.format(today))

##########

## TUMBLR FUNCTIONS
def entryMacroTumblrLog(name, link1):
	client.create_link("si507-log", title="{}'s Entry Macronutrient Log for {}".format(name, today), url="{}".format(link1))

def dailyMacroTumblrLog(name, link2):
	client.create_link("si507-log", title="{}'s Daily Macronutrient Log for {}".format(name, today), url="{}".format(link2))

def dailyCalTumblrLog(name, link3):
	client.create_link("si507-log", title="{}'s Daily Calorie Log for {}".format(name, today), url="{}".format(link3))

def dailyGoalTumblrLog(name, link4):
	client.create_link("si507-log", title="{}'s Daily Goal Log for {}".format(name, today), url="{}".format(link4))

##########

def presentable_data(daily_dict, cal_goal):
	## CREATING CLASS INSTANCES FROM EACH ITEM IN DAILY FOOD DICTIONARY
	entries = []
	for item in daily_dict:
		dict_list = []
		dict_list.append(item)
		dict_list.append(daily_dict[item][0])
		dict_list.append(daily_dict[item][1])
		dict_list.append(daily_dict[item][2])
		dict_list.append(daily_dict[item][3])
		dict_list.append(daily_dict[item][4])
		dict_list.append(daily_dict[item][5])

		classEntry = logEntry(dict_list[0], dict_list[1], dict_list[2], dict_list[3], dict_list[4], dict_list[5], dict_list[6])
		entries.append(classEntry)
	return entries

def ploty_data_calls(entries, cal_goal):
	## CREATING LISTS OF DAILY ENTRY NAMES, CALORIES, PROTEIN, FAT, & CARBS
	entryNames = []
	entryCals = []
	entryProtein = []
	entryFat = []
	entryCarbs = []

	for item in entries:
		entryNames.append(item.name)
		entryCals.append(item.cals)
		entryProtein.append(item.protein)
		entryFat.append(item.fat)
		entryCarbs.append(item.carbs)

	dailyCals = 0
	for item in entryCals:
		dailyCals = (int(item) + dailyCals)

	dailyProtein = 0
	for item in entryProtein:
		dailyProtein = (float(item) + dailyProtein)

	dailyFat = 0
	for item in entryFat:
		dailyFat = (float(item) + dailyFat)

	dailyCarbs = 0
	for item in entryCarbs:
		dailyCarbs = (float(item) + dailyCarbs)

	dailyMacros = [dailyProtein, dailyFat, dailyCarbs]

	## CALLING PLOTLY FUNCTIONS
	entryMacroPlot(entryNames, entryProtein, entryFat, entryCarbs)
	dailyMacroPlot(dailyMacros)
	dailyCalPlot(entryNames, entryCals)
	dailyGoalPlot(cal_goal, dailyCals)

def interactive_prompt():
	daily_dict = {}
	name = input("What's your name?: ")
	cal_goal = input("What is your daily calorie goal?: ")
	try:
		cal_goal = int(cal_goal)
	except Exception:
		cal_goal = input("Please enter an integer for your daily calorie goal: ")
	start = input("Do you want to start your daily log? Enter 'yes' or 'no': ")
	while start != 'no':

		food = input("What do you want to log? (Enter 'close' to close today's log.): ")
		if food != 'close':
			try:
				results = populate_tables(food)

				statement = '''
					SELECT NutritionalInfo.FoodName, NutritionalInfo.Calories, NutritionalInfo.ServSize, NutritionalInfo.ServMeasure, NdbNums.UPC, NutritionalInfo.Protein, NutritionalInfo.Fat, NutritionalInfo.Carbs
				    FROM NutritionalInfo
				    JOIN NdbNums ON NdbNums.Ndb = NutritionalInfo.FoodNdb
				    WHERE NutritionalInfo.FoodName = NdbNums.FoodName
				    '''	
				item_count = 0
				item_choice_dict = {}
				item_nut_dict = {}
				item_upc_dict = {}
				item_cal_dict = {}
				item_serv_dict = {}
				for row in cur.execute(statement):
					item_count += 1
					item_choice_dict[item_count] = row[0]
					item_cal_dict[row[0]] = row[1]
					item_serv_dict[row[0]] = row[2]
					item_nut_dict[row[0]] = row[1], row[2], row[3], row[5], row[6], row[7]
					item_upc_dict[row[0]] = str(row[4])

				print("===================")
				print("AVAILABLE OPTIONS")
				for item in item_choice_dict:
					if int(item) <= 25:
						print(item, item_choice_dict[item])
				print("===================")

				choice = input("Enter the number of the item you want to log, or, if the item you want to log is not on this list, enter 'redo' to enter a more specific search term: ")
				if choice == 'redo':
					pass				
				else:
					try:
						choice = int(choice)
						if choice in list(item_choice_dict.keys()):
							add_choice = input("Is '{}' what you want to log? Enter 'yes', 'no', or 'unsure': ".format(item_choice_dict[choice]))
							if add_choice == 'yes':		
								daily_dict[item_choice_dict[choice]] = item_nut_dict[item_choice_dict[choice]]
								print("Item added to daily log.")
							elif add_choice == 'no':
								pass
							elif add_choice == 'unsure':
								print("===================")
								print("Here's the UPC code and caloric information for this item so you can check whether you really do want to log it: \nUPC: {} \nCALORIC INFORMATION: {} calories per {}g".format(item_upc_dict[item_choice_dict[choice]], item_cal_dict[item_choice_dict[choice]], item_serv_dict[item_choice_dict[choice]]))
								print("===================")
								answer_a = input("So, do you want to log this item? Enter 'yes' or 'no': ")
								if answer_a == 'yes':
									daily_dict[item_choice_dict[choice]] = item_nut_dict[item_choice_dict[choice]]
									print("Item added to daily log.")
								elif answer_a == 'no':
									pass
							else:
								print("Enter a valid command.")
						else:
							print("Enter a valid command.")
					except Exception:
						print("Enter a valid command.")
			except Exception:
				print("Enter a valid item name. (You may want to check your spelling.)")
		else:
			print("Today's log has been closed.")
			break
	
	if start == 'no':
		sys.exit()

	ploty_data_calls(presentable_data(daily_dict, cal_goal), cal_goal)

	## GETTING USER INPUT FOR EACH PLOTLY VISUALIZATION LINK & CALLING TUMBLR FUNCTIONS
	link1 = input("Enter the link to the Entry Macronutrients plot.ly visualization: ")
	try:
		entryMacroTumblrLog(name, link1)
		print("Visualization posted to si507-log.tumblr.com!")
	except Exception:
		print("Visualization failed.")


	link2 = input("Enter the link to the Daily Macronutrients plot.ly visualization: ")
	try:
		dailyMacroTumblrLog(name, link2)
		print("Visualization posted to si507-log.tumblr.com!")
	except Exception:
		print("Visualization failed.")

	link3 = input("Enter the link to the Daily Calories plot.ly visualization: ")
	try:
		dailyCalTumblrLog(name, link3)
		print("Visualization posted to si507-log.tumblr.com!")
	except Exception:
		print("Visualization failed.")

	link4 = input("Enter the link to the Daily Goal plot.ly visualization: ")
	try:
		dailyGoalTumblrLog(name, link4)
		print("Visualization posted to si507-log.tumblr.com!")
	except Exception:
		print("Visualization failed.")


if __name__=="__main__":
    interactive_prompt()
