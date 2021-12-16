from uk_covid19 import Cov19API
import sched, time, json, logging

covid_data = {
    'National_7_day_cases': 0,
    'National_hospital_cases': 0,
    'National_deaths': 0,
    'Local_7_day_cases': 0
}

logging.basicConfig(filename = "covid_dashboard.log", level = logging.WARNING, format = "%(asctime)s:%(levelname)s:%(message)s")        # Logs the programs running in the log file.

try:
    with open("config.json", "r") as jsonfile:          # Loads the config.json file into a global dictionary.
        config = json.load(jsonfile)
except:
    logging.error("ERROR ACCESSING CONFIG FILE")

location_national = config['location_national']
location_local = config['location_local']

def parse_csv_data(csv_filename: str):
    '''Reads in the data from the csv file specified by the parameter 'csv_filename'
    and returns a list of dictionaries containing the covid data.'''
    import csv
    
    with open(csv_filename, "r") as file:       # Sets 'file' as a function to open and view the .csv file.

        csv_data = []                           # Initialises the array that will hold the lists of each row from the .csv file, each row being 1 element in the list.
        i = 0
        reader = csv.reader(file)
        for row in reader:
            csv_data.append(row)
            i += 1

    return csv_data

def process_covid_csv_data(covid_csv_data: list):
    '''Takes the list of dictionaries and processes it to find and
    return the 7 day cases, hospital cases, and total deaths.'''
    days_with_cases_data = 0
    hosp_cases_found = False
    total_deaths_found = False
    seven_day_cases = 0
    
    for i in range(1, (len(covid_csv_data) - 1)):                           # Skips the header of the .csv file with the column names.
        csv_line = ""
        csv_line = str(covid_csv_data[i])
        csv_values_arr = csv_line.strip("[]").split("\', \'")
        csv_values_arr[6] = csv_values_arr[6][:-1]
        
        if days_with_cases_data < 7:                                        # Ensures only the first 7 values are added.
            if csv_values_arr[6] != "" and csv_values_arr[6] != "8786":     # Ensures no non-empty values are added.
                days_with_cases_data += 1
                seven_day_cases += int(csv_values_arr[6])                   # Adds the first 7 non-empty values of newCasesBySpecimenDate to get the number of cases in the last 7 days.

        if hosp_cases_found == False and csv_values_arr[5] != "":           # Ensures only the first non-empty value of hospital cases is taken.
            hosp_cases = int(csv_values_arr[5])                             # Current hospital cases
            hosp_cases_found = True

        if total_deaths_found == False and csv_values_arr[4] != "":         # Ensures only the first non-empty value of cumulative deaths is taken.
            total_deaths = int(csv_values_arr[4])
            total_deaths_found = True
            
        if days_with_cases_data > 6 and hosp_cases_found == True and total_deaths_found == True:    # Breaks out of the loop as soon as all the required data has been found and saved into variables.
            break

    return seven_day_cases, hosp_cases, total_deaths

def covid_API_request(location: str = location_local, location_type: str = "ltla"):
    '''Takes the location, with the default being the 'location_local' specified in the
    config file, and location type, with the default being 'local authority' and searches
    through the 'Cov19API' to return a dictionary of the relevant values for the location 
    specified in the parameters.'''

    area = [
        f"areaType={location_type}",
        f"areaName={location}"
    ]

    cases_and_deaths = {
    "areaCode": "areaCode",
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",
    "totalDeaths": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases",
    "newCasesByDate": "newCasesBySpecimenDate"
}
    
    api = Cov19API(filters=area, structure=cases_and_deaths)            # Accesses the API and loads the data into a dictionary.
    covid_data_dict = api.get_json()

    return covid_data_dict
    
def seven_day_cases_calc_json(covid_data_dict: dict):
    '''Takes the dictionary of values from the 'Cov19API' and calculates
    the total cases from the first day with data and 6 days after.'''
    seven_day_cases = 0
    i = 0
    while covid_data_dict['data'][i]['newCasesByDate'] is None:
        i += 1
    i += 1
    for day in range(i, i+7):
        seven_day_cases += covid_data_dict['data'][day]['newCasesByDate']

    return seven_day_cases
    
def hosp_cases_calc_json(covid_data_dict: dict):
    '''Takes the dictionary of values from the 'Cov19API' and finds the
    total number of hospital cases from the earliest date with data.'''
    i = 0
    length_data = len(covid_data_dict['data'])
    while i < length_data and covid_data_dict['data'][i]['hospitalCases'] is None:
        i += 1

    hosp_cases = covid_data_dict['data'][i]['hospitalCases']
    
    return hosp_cases
    
def total_deaths_calc_json(covid_data_dict: dict):
    '''Takes the dictionary of values from the 'Cov19API' and finds the
    total number of deaths with the most up to date data.'''
    i = 0
    length_data = len(covid_data_dict['data'])
    while covid_data_dict['data'][i]['totalDeaths'] is None:
        i += 1

    total_deaths = covid_data_dict['data'][i]['totalDeaths']
    
    return total_deaths
    
def load_national_covid_data_json(covid_data_dict: dict):
    '''Takes the dictionary of values from the 'Cov19API' and uses it as a parameter to load all of
    the data into one function, returning all of the data as 3 variables so it is easier to handle.'''
    try:
        seven_day_cases = seven_day_cases_calc_json(covid_data_dict)
        hosp_cases = hosp_cases_calc_json(covid_data_dict)
        total_deaths = total_deaths_calc_json(covid_data_dict)
    except:
        logging.error("COULD NOT PROCESS NATIONAL STATS DATA")
    
    return seven_day_cases, hosp_cases, total_deaths

def update_covid_data():
    '''Updates the covid_data using the API and stores it in a dictionary, which is returned.'''
    global covid_data

    try:
        national_covid_data = load_national_covid_data_json(covid_API_request(location_national, 'nation'))     # Loads the national stats for the nation chosen in the config file.
    except:
        logging.error("ERROR LOADING NATIONAL STATS")
    local_covid_data = seven_day_cases_calc_json(covid_API_request())       # Loads the local stats for the local authority area chosen in the config file.
    

    covid_data = {
        'National_7_day_cases': national_covid_data[0],
        'National_hospital_cases': national_covid_data[1],
        'National_deaths': national_covid_data[2],
        'Local_7_day_cases': local_covid_data
}

    logging.warning("COVID DATA UPDATED")

    return covid_data

def schedule_covid_updates(update_interval: int, update_name: str, user_update_data: bool = True, user_update_news: bool = True):
    '''Takes the update interval, name, whether the data and/or news will be updated and schedules an update for the specified time.'''
    from main import update_request                 # Prevents circular import error.
    
    s = sched.scheduler(time.time, time.sleep)

    
    s.enter(update_interval, 1, update_request, (user_update_data, user_update_news))