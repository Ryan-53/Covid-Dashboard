from flask import Flask, render_template, request
from covid_news_handling import update_news
from covid_data_handler import update_covid_data, schedule_covid_updates
import sched, time, datetime, json, logging
from PIL import Image
from test_covid_data_handler import tests_data_handler
from test_news_data_handling import tests_news_handling

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)
deleted_news_articles = []
news = update_news(deleted_news_articles)                            # Loads the most up to date news and data so it  #
covid_data = update_covid_data()                # can be displayed when the webpage is launched. #
scheduled_update_list = []
deleted_updates = []
scheduled_bool = True
update_repeated = False

logging.basicConfig(filename = "covid_dashboard.log", level = logging.WARNING, format = "%(asctime)s:%(levelname)s:%(message)s")        # Logs the programs running in the log file.
logging.disable(logging.INFO)                           # Stops the URL and refresh data being logged every minute.

try:
    with open("config.json", "r") as jsonfile:          # Loads the config.json file into a global dictionary.
        config = json.load(jsonfile)
except:
    logging.error("ERROR ACCESSING CONFIG FILE")

location_national = config['location_national']
location_local = config['location_local']
title_str = config['title_str']
logo_path = config['logo_path']
favicon_path = config['favicon_path']

def calc_update_interval(update_time: str):
    '''Takes time input by user and calculates difference with current time to return the update interval (time until the update should be carried out)'''
    update_time_arr = update_time.split(":")
    update_time_hr = int(update_time_arr[0])                                    # Separates the update_time returned by the webpage into integer variables.
    update_time_min = int(update_time_arr[1])
    
    try:
        current_time = datetime.datetime.now()
    except:
        logging.error("COULD NOT FETCH CURRENT TIME")
    current_hr = int(current_time.strftime("%H"))                               # Calculates current time and separates it into integer variables
    current_min = int(current_time.strftime("%M"))
    

    update_time_secs = (update_time_hr * 3600) + (update_time_min * 60)         # Calculates time in seconds.
    current_time_secs = (current_hr * 3600) + (current_min * 60)
    update_interval = update_time_secs - current_time_secs                      # Calculates time difference between current and scheduled update time.

    if update_time_secs < current_time_secs:                                    # If the update time is scheduled as before the current time, then the time interval is recalculated, so it is correct.
        update_interval = ((60 * 60 * 24) - update_interval) + update_time_secs
            
    return update_interval

def update_request(user_update_data: bool, user_update_news: bool, deleted_news_articles: list = [], update_label: str = None, update_repeated: bool = False):
    '''Takes in whether the user wants to update data and/or news, the names of the news articles the
    user has deleted, the name of the update, and whether the update is set to be repeated 24 hours later,
    and therefore updates the relevant dictionaries and lists to update the data, ensures deleted updates
    are not carried out, and removes the updates from the scheduled updates column if they are due to be removed. '''
    global covid_data, news, deleted_updates
    delete_update = False

    try:
        for i in range(len(deleted_updates)):
            if update_label == deleted_updates[i]:                          # Checks whether the update has been cancelled and if so, doesn't perform
                delete_update = True                                        # the update and removes the name from the 'deleted_updates' list so  
                logging.warning("UPDATE SET FOR DELETION")                  # it can be used again as an update label for a new scheduled update.
                try:
                    if update_repeated == False:
                        deleted_updates.pop(i)
                except:
                    logging.error("COULD NOT REMOVE UPDATE NAME FROM LIST")
    except:
        logging.error("ERROR DELETING UPDATE")

    if delete_update == False:
        try:
            if user_update_data == True:
                try:
                    covid_data = update_covid_data()                            # Updates news and covid data.
                except:
                    logging.error("ERROR UPDATING DATA")
        except:
            logging.error("NO VARIABLE PASSED IN FOR 'user_update_data'")
        try:
            if user_update_news == True:
                try:
                    news = update_news(deleted_news_articles)
                except:
                    logging.error("ERROR UPDATING NEWS ARTICLES")
        except:
            logging.error("NO VARIABLE PASSED IN FOR 'user_update_news'")

        if update_label:
            delete_scheduled_update(update_label, update_repeated, True)      # Removes the scheduled update object from the webpage.

def delete_news_article(delete_news_article_name: str, news: list):
    '''Takes the name of the article to delete and the list of dictionaries containing 
    news articles currently loaded in and returns the new list of dictionaries of news
    articles with the deleted news article excluded from it as well as updating a list
    of deleted news articles to ensure it is not included in any future updates.'''
    global deleted_news_articles

    try:
        delete_news_article_index = next((i for i, item in enumerate(news) if item["title"] == delete_news_article_name), None)     # Searches through the list of news articles loaded in to find the index of news article the user wants to remove.
    except:
        logging.error("ERROR ITERATING THROUGH 'news'")
    
    try:
        news.pop(delete_news_article_index)                                 # Removes the news article chosen to be removed by the user, from the list so it is not displayed after the page refreshes.
        deleted_news_articles.append(delete_news_article_name)              # Adds the name of the deleted article to a list which is used to exclude that article from later updates.
        logging.warning("NEWS ARTICLE DELETED")
    except:
        logging.error("ARTICLE TO DELETE NOT FOUND IN 'news'")

    return news

def delete_scheduled_update(update_label: str, update_repeated: bool = False, update_remove: bool = False):
    '''Takes the name of the update to be deleted, whether it has been repeated and if itis just
    to be removed after the update was completed., it then removes it from the scheduled update column.'''
    global scheduled_update_list, deleted_updates

    try:
        scheduled_update_index = next((i for i, item in enumerate(scheduled_update_list) if item["title"] == update_label), None)
    except:
        logging.error("ERROR ITERATING THROUGH 'scheduled_update_list'")

    if scheduled_update_index != None and update_repeated == False:
        scheduled_update_list.pop(scheduled_update_index)                   # Removes the scheduled update object from the list which will be displayed on the webpage.

    if update_repeated == True:
        for i in range(len(deleted_updates)):
            if update_label == deleted_updates[i]:                          # Removes the name of the cancelled scheduled update from the list 'deleted_updates', so the same update label can be used again without any errors.
                deleted_updates.pop(i)

    if update_repeated == False:
        if update_remove == False:
            logging.warning("SCHEDULED UPDATE DELETED")
        else:
            logging.warning("SCHEDULED UPDATE REMOVED AFTER COMPLETION")

def update_repeat(user_update_data: bool, user_update_news: bool, deleted_news_articles: list, update_label: str = None):
    '''Takes in whether the user wants to update data and/or news, the names of the news articles the
    user has deleted,and the name of the update, then it schedules an update for 24 hours in the future
    and schedules an event for the same amount of time to call itself'''
    s.enter((60 * 60 * 24), 1, update_request, (user_update_data, user_update_news, deleted_news_articles, update_label, True))       # Runs the scheduled update 24 hours after the previous one.
    s.enter((60 * 60 * 24), 1, update_repeat, (user_update_data, user_update_news, deleted_news_articles, update_label))        # Schedules the next update for 24 hours from then.
    logging.warning("REPEAT UPDATE SCHEDULED")

@app.route('/')
@app.route('/index')
def html():
    '''Runs the webpage; checks the address for certain values and
    calls certain functions and schedules functions accordingly.'''
    global news, covid_data, deleted_updates

    s.run(blocking=False)                                                   # Runs the scheduled tasks if they are due to be executed at that time.
    user_update_data = False
    user_update_news = False
    update_label = request.args.get('two')                                  # Returns the update label that the user called their submitted update.
    delete_news_article_name = request.args.get('notif')
    delete_scheduled_update_name = request.args.get('update_item')

    if update_label:
        logging.warning("UPDATE SUBMITTED")
        update_time = request.args.get('update')
        update_data_request = request.args.get('covid-data')                # Returns the values the webpage produces when the user presses submit.
        update_news_request = request.args.get('news')
        update_repeat_request = request.args.get('repeat')

        update_content = update_time
        if update_data_request:
            user_update_data = True
            update_content += " - Covid data"
            logging.warning("COVID DATA UPDATE REQUESTED")
        if update_news_request:                                             # Checks what things the user selected to update or whether to repeat and
            user_update_news = True                                         # outputs a description accordingly on the scheduled updates object.
            update_content += " - News articles"
            logging.warning("NEWS UPDATE REQUESTED")
        if update_repeat_request:
            update_content += " - REPEATING DAILY"
            logging.warning("REPEAT UPDATE REQUESTED")

        if update_time == '':
            update_request(user_update_data, user_update_news, deleted_news_articles)       # Instantly updates data and/or news if the user didn't schedule a time.

        else:
            logging.warning("UPDATE SCHEDULED")
            update_interval = calc_update_interval(update_time)             # Calculates difference in time between current time and the newly scheduled update time.
            scheduled_update_list.append(
                {
                    'title': update_label,                                  # Adds the update name, time and type (data and/or news) to the
                    'content': update_content                               # list which will be displayed in the scheduled updates column.
                }
                )
            
            if update_repeat_request:
                update_repeated = True
                try:
                    s.enter(update_interval, 1, update_repeat, (user_update_data, user_update_news, deleted_news_articles, update_label))      # Schedules a function that updates 24 hours after the given time, and then schedules the
                except:
                    logging.error("COULD NOT SCHEDULE A REPEAT OF THE UPDATE")
            else:
                update_repeated = False

            s.enter(update_interval, 1, update_request, (user_update_data, user_update_news, deleted_news_articles, update_label, update_repeated))         # Schedules the update at the given interval.

    if delete_news_article_name:
        logging.warning("DELETE NEWS ARTICLE REQUESTED")
        news = delete_news_article(delete_news_article_name, news)          # Updates the news dictionary to not include the deleted news article.

    if delete_scheduled_update_name:
        logging.warning("DELETE SCHEDULED UPDATE REQUESTED")
        delete_scheduled_update(delete_scheduled_update_name)               # Cancels the scheduled update and ensures it isn't repeated if it is set as a repeating update.
        deleted_updates.append(delete_scheduled_update_name)

    try:
        return render_template('index.html',
            title= title_str,
            news_articles = news,
            location = location_local,
            local_7day_infections = covid_data['Local_7_day_cases'],
            nation_location = location_national,
            national_7day_infections = covid_data['National_7_day_cases'],
            hospital_cases = 'Hospital cases: ' + str(covid_data['National_hospital_cases']),
            deaths_total = 'Total deaths: ' + str(covid_data['National_deaths']),
            updates = scheduled_update_list,
            image = logo_path,
            favicon = favicon_path)
    except:
        logging.critical("COULD NOT UPDATE WEBPAGE")

try:
    if __name__ == '__main__':                          # Runs the flask application that works with the webpage.
        app.run()
except:
    logging.critical("COULD NOT RUN FLASK SCRIPT")

### TESTS ###

def test_empty_update_request():
    '''Checks to ensure the 'update_request' function doesn't do
    anything if it is passed values of 'False' to update data or news'''
    global covid_data, news

    local_covid_data = covid_data
    local_news = news

    update_request(user_update_data = False, user_update_news = False)

    assert local_covid_data == covid_data
    assert local_news == news

def tests_main():
    test_empty_update_request()

def daily_tests():
    tests_data_handler()
    tests_news_handling()
    tests_main()

def schedule_daily_tests():
    '''Schedules a test for 24 hours time and schedules the function to be called again to schedule another test in 24 hours.'''
    s.enter((60 * 60 * 24), 1, daily_tests)
    s.enter((60 * 60 * 24), 1, schedule_daily_tests)
    
daily_tests()               # Performs all of the tests when the program is first ran.
schedule_daily_tests()