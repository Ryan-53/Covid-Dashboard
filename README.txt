### READ ME FOR COVID DASHBOARD ###

## TO USE ##

1. Run main.py
2. Go to http://127.0.0.1:5000

Updates to covid data and covid news can be scheduled for a specified time
by inputting the time in the box with a clock in it or done instantly if
you don't put anything in the box.

Updates must have a name so they can be tracked, the name can be anything.

Updates can also be repeated, this means that the update will take place
every day at the specified time until it is cancelled or the program is
terminated.

## FOR DEVELOPERS ##

# CONFIG FILE #

Holds:
	The national and local locations - locations to get covid data for.
	Covid key terms - queries that will be used to get news articles.
	API url - url to the news API to get news articles from.
	API key - key used to access the news API.
	Language to get news articles in.
	Title on the webpage.
	Paths to the images of the logo on the website and the favicon.

These can be changed by editing them in the config.json file in the directory.

# LOG FILE #

WARNING is logged during normal use in order to exclude the log file being filled
with URL dumps every minute and every refresh.