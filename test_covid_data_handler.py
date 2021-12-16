from covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request, schedule_covid_updates, update_covid_data

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_covid_data_present():
    '''Checks whether the 'update_covid_data' function 
    works by checking it doesn't return empty values.'''
    covid_data = update_covid_data()
    assert isinstance(covid_data, dict)
    assert covid_data['National_7_day_cases'] != None
    assert covid_data['National_hospital_cases'] != None
    assert covid_data['National_deaths'] != None
    assert covid_data['Local_7_day_cases'] != None

def tests_data_handler():
    '''Compiles all of the tests on the 'covid_data_handler' module into 1 function so it
    can be executed and scheduled more easily in the 'main' module for regular tests.'''
    test_parse_csv_data()
    test_process_covid_csv_data()
    test_covid_API_request()
    test_schedule_covid_updates()
    test_covid_data_present()