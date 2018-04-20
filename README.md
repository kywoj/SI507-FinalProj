# Daily Nutrition Visualization Log#

## User Guide ##
This **Daily Nutrition Visualization Log** program prompts you to enter the foods you've eaten throughout any given day and then provides four different types of visualizations to allow you to track your progress toward your nutritional goals.

Start by entering your name and your daily calorie goal when prompted. 

*Note*: You can use this [Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) Calculator] (https://www.sailrabbit.com/bmr/) if you're not sure how many calories you should be eating per day to meet your goal of losing, maintaining, or gaining weight. Be sure to consult with a physician before starting any type of diet.

Then, you'll be asked if you want to start your daily log, so enter 'yes' or 'no'.

Then, you'll be asked which food you want to log, and you can just enter its name: 'baby carrots' or 'vanilla yogurt', for example. The top 25 options will be displayed, with a number next to each. 

You'll be prompted to enter either 

* the number that corresponds to the food you want to log, **or**
* 'redo', in case the food you want to log doesn't appear in the search results. If this happens, you should enter a more specific search term when you're prompted again.

When you've entered the number that corresponds to the food you want to log, you'll be asked to confirm whether you want to log it. You can enter 'yes' to add the food to your daily log, 'no' to enter a new food, or 'unsure' if you'd like to double-check that the food's UPC and calorie count match that which you want to add to your log.

After you've finished adding all the food you want to log for the day, enter 'close' to close the log.

Four different visualizations will then be created based on the nutritional content of the foods you've logged:

1. **Entry Macronutrient Log**, which displays (in grams) the amount of protein, fat, and carbs in each of the foods you logged this day

2. **Daily Macronutrient Log**, which displays (in grams) the total amount of protein, fat, and carbs you logged this day

3. **Daily Calorie Log**, which displays the calorie count of each food you logged this day

3. **Daily Goal Log**, which displays the number of calories you logged this day in comparison to your daily calorie goal.

Finally, you'll be prompted to copy and paste the links to each of these visualizations, and they will be added as individual posts to your [Tumblr blog] (https://si507-log.tumblr.com/) for tracking purposes.


## Code Structure Description ##
### Significant Data Processing Functions###
Save for the functions that create caches, create the database and tables, and define the actions taken with the Plot.ly and Tumblr APIs, the following are descriptions of the most significant data processing functions in this program:

* The **populate_tables** function takes in a user's search query as input, running that through the USDA NBD API (or cache) and then the USA Food Report API (or cache). It then populates the **food.db** database with two tables: 'NdbNums' and 'NutritionalInfo', with 5 and 10 fields respectively.
* The **interactive_prompt** function prompts a user to enter their name, daily calorie goal, and food search query. It then displays the results of their query, builds the database tables around the their selected query, and adds the their logged entries to the **daily_dict** dictionary. 

 * Then, the **presentable_data** function (described below) and the**ploty\_data\_calls** functions are called, and users are prompted to enter the URLs of the resulting Plot.ly visualizations so as to create daily posts on their Tumblr blog.

### Large Data Structure & Class Definition ###
Each food item that a user chooses to add to their daily log is stored in a dictionary called **daily_dict**, where the key is the food name and the values are the food's calorie count, default serving size, default serving measure, and grams of protein, fat, and carbs.

 The **presentable_data** function takes each item from the ** daily_dict** dictionary and creates instances of the class **logEntry**, which has seven instance variables and a string method that looks like this:

>> {} has {} calories per {}{}, with {}g of protein, {}g of fat, and {}g of carbs


## Data Sources ##
### USDA ###
First, you'll need a [USDA API Key] (https://ndb.nal.usda.gov/ndb/doc/index#) to use the 

* [NBD API] (https://ndb.nal.usda.gov/ndb/doc/apilist/API-SEARCH.md) to search for each food's NDB (National Database) number.
* [Food Report API] (https://ndb.nal.usda.gov/ndb/doc/apilist/API-FOOD-REPORT.md) to use enter a food's NDB number to get its nutritional information.

You should put the API key in a file called ** usda_secrets.py**, and format the file's contents accordingly:
>> usda_key = 'API-KEY-HERE'

Be sure to include **import usda_secrets** in your program file.

### Tumblr ###
Then, you'll need to register the application to get a [Tumblr consumer key & secret and OAuth token & secret] (https://www.tumblr.com/oauth/apps).

You should put the API key in a file called ** tumblr_secrets.py**, and format the file's contents accordingly:

>> consumer_key = 'CONSUMER-KEY-HERE'

>> consumer_secret = 'CONSUMER-SECRET-HERE'

>> oauth_token = 'OAUTH-TOKEN-HERE'

>> oauth_secret = 'OAUTH-SECRET-HERE'

Be sure to include **import tumblr_secrets** in your program file.

*Note*: You'll also need to create a Tumblr blog so that you can use the [**/post** method] (https://www.tumblr.com/docs/en/api/v2#posting) in this program.

### Plotly ##
Finally, you'll also need [Plot.ly account and API key] (https://plot.ly/python/getting-started/), which you'll be prompted for when you **import plotly**.

Don't forget to declare your keys and tokens in your program file.