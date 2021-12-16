from covid_news_handling import news_API_request, update_news
import logging

logging.basicConfig(filename = "covid_dashboard.log", level = logging.WARNING, format = "%(asctime)s:%(levelname)s:%(message)s")

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_articles():
    '''Checks whether the 'news_API_request' function will return
    at least 1 news article to make sure it is still working.'''
    try:
        news_articles = news_API_request
        assert len(news_articles) > 0
    except:
        logging.error("NO NEWS ARTICLES RETURNED BY THE API REQUEST")

def tests_news_handling():
    '''Compiles all of the tests on the 'covid_news_handling' module into 1 function so it
    can be executed and scheduled more easily in the 'main' module for regular tests.'''
    test_news_API_request()
    test_update_news()
    test_articles()