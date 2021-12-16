import requests, sched, time, json, logging

logging.basicConfig(filename = "covid_dashboard.log", level = logging.WARNING, format = "%(asctime)s:%(levelname)s:%(message)s")        # Logs the programs running in the log file.

logging.warning("ACCESSING CONFIG FILE")
try:
    with open("config.json", "r") as jsonfile:          # Loads the config.json file into a global dictionary.
        config = json.load(jsonfile)
except:
    logging.error("ERROR ACCESSING CONFIG FILE")

covid_key_terms = config['covid_key_terms']
api_url = config['api_url']
api_key = config['api_key']
language = config['language']

def news_API_request(covid_terms: str = covid_key_terms):
    '''Takes the keyword terms with a default value of the 'covid_key_terms' from the config file,
    and makes a query with the news API specified in the config file for news articles in the 
    language specified in the config file, using the API key specified in the config file, generating
    a list of dictionaries of news articles that is returned.'''
    query = covid_terms.split(" ")                          # Splits up queries into strings that can be queried individually.
    news_articles = []

    try:
        for i in range(len(query)):
            response = requests.get(api_url, {              # It will load in news articles from the url given in the config file.
               'apiKey': api_key,                           # Uses the API key in the config file.
               'language': language,                        # Only gets news in the language set in the config file.
               'q': query[i]                                # Gets news articles that have the query of any of the queries set in the config file.
            } ).json()                                      # Accesses each article as a json file.

            news_articles += response["articles"]           # Compiles all articles into a list of dictionaries.
    except:
        logging.error("ERROR ACCESSING NEWS API")
    
    return news_articles

def update_news(deleted_news_articles: list = []):
    '''Takes a list of news articles the user has deleted and returns
    a list of news articles excluding any the user has deleted.'''
    news_articles = {}
    news_articles = news_API_request()
    news_articles_deleted = 0
    for counter in range(len(deleted_news_articles)):
        try:
            exclude_article_index = next((i for i, item in enumerate(news_articles) if item["title"] == deleted_news_articles[counter]), None)      # Searches through the list of news articles about to be loaded in to find the index of news article the user wants to remove.
        except:
            logging.error("ERROR ITERATING THROUGH 'news_articles'")

        if exclude_article_index != None:
            news_articles.pop(exclude_article_index)                # Removes the news article from the list so it is not displayed when the user performs a news update.
            news_articles_deleted += 1

        if news_articles_deleted != 0:
            logging.warning("DELETED ARTICLES FOUND IN UPDATE")
            logging.warning("USER DELETED NEWS ARTICLES HAVE BEEN EXCLUDED FROM UPDATE")

    logging.warning("NEWS UPDATED")
    
    return news_articles