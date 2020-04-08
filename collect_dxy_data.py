from bs4 import BeautifulSoup
import requests
import sqlite3
import urllib
import xlrd
import os
import datetime
import pandas as pd
from googlemaps import Client as GoogleMaps

def get_coronavirus_data():
    file_path = 'data/virus_data.xls'

    wb = xlrd.open_workbook(file_path)
    sheet_names = wb.sheet_names()
    s = wb.sheet_by_name(sheet_names[0])

    data_list = []

    for i in range(2, len(s.col_values(0))):

        good_data = True

        data_entry = dict()

        # 1. Gets the entry ID
        entry_id = s.cell_value(i, 0)
        if entry_id is '':
            good_data = False
        else:
            entry_id = int(entry_id)
        data_entry["id"] = entry_id

        # 2. Reporting Date:
        report_date_raw = s.cell_value(i, 2)
        if len(str(report_date_raw)) > 2:
            report_date = xlrd.xldate_as_tuple(report_date_raw, wb.datemode)
            data_entry["report_date"] = report_date
        else:
            good_data = False

        # 3. Summary:
        summary = s.cell_value(i, 3)
        data_entry["summary"] = summary

        # 4. City:
        city = s.cell_value(i, 4)
        if len(city) == 0:
            good_data = False
        data_entry["city"] = city

        # 5. Country:
        country = s.cell_value(i, 5)
        if len(country) == 0:
            good_data = False
        data_entry["country"] = country

        # 6. Gender:
        gender = s.cell_value(i, 6)
        if len(gender) <= 2:
            good_data = False
        data_entry["gender"] = gender

        # 7. Age:
        age = s.cell_value(i, 7)
        if str(age) == 'NA' or str(age) == '':
            good_data = False
        else:
            data_entry["age"] = int(age)

        # 8. Visiting from Wuhan
        visiting = str(s.cell_value(i, 15))
        if visiting == 'NA' or visiting == '':
            good_data = False
        else:
            if visiting == '1.0':
                data_entry["visiting_wuhan"] = True
            elif visiting == '0.0':
                data_entry["visiting_wuhan"] = False

        # 9. From Wuhan
        from_wuhan = str(s.cell_value(i, 16))
        if from_wuhan == 'NA' or from_wuhan == '':
            good_data = False
        else:
            if from_wuhan == '1.0':
                data_entry["from_wuhan"] = True
            elif from_wuhan == '0.0':
                data_entry["from_wuhan"] = False
            else:
                good_data = False

        # 10. Death:
        death = str(s.cell_value(i, 17))
        if death == 'NA' or death == '' or death is None:
            good_data = False
        else:
            if death == '1.0' or len(death) > 4:
                data_entry["death"] = True
            else:
                data_entry["death"] = False

        # Appends entry if it is valid data
        if good_data:
            data_list.append(data_entry)

    return data_list

def create_virus_table():
    # Create connection to database
    conn = sqlite3.connect('data/data.db')
    c = conn.cursor()

    # Delete tables if they exist
    c.execute('DROP TABLE IF EXISTS "virus_data";')

    # Create table in the database and add data to it
    create_virus_table_command = '''
    CREATE TABLE IF NOT EXISTS virus_data (
    	id INT NOT NULL,
    	report_date DATE NOT NULL,
    	summary VARCHAR(200),
        city VARCHAR(50) NOT NULL,
        country VARCHAR(50) NOT NULL,
        gender VARCHAR(10) NOT NULL,
        age INT NOT NULL,
        visiting_wuhan  BOOLEAN NOT NULL,
        from_wuhan BOOLEAN NOT NULL,
        death BOOLEAN NOT NULL,
    	PRIMARY KEY (id)
    );
    '''

    # # Creates the virus_data tables
    c.execute(create_virus_table_command)

    # Fills in tables with data from stock information
    for i in get_coronavirus_data():
        cur_date = i["report_date"]
        date = datetime.date(cur_date[0], cur_date[1], cur_date[2])
        c.execute('''INSERT INTO virus_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (i["id"], date, i['summary'], i['city'], i['country'], i['gender'], i['age'], i['visiting_wuhan'], i['from_wuhan'], i['death']))

    # Commits out changes to the database.
    conn.commit()
    print('Virus table created!')


def create_environment_table():
    TOKEN = '1e50020499453cb7462d5da1ab16c69cb0fb86a7'
    # GMAPTOKEN = 
    # put google api key above
    # WEATHER_TOKEN =     
    # # put weather api key here
    exclude_weather = '[currently, minutely, hourly]'

    gmaps = GoogleMaps(GMAPTOKEN)

    URL_AQI = 'https://api.waqi.info/feed/'
    URL_WEATHER = 'https://api.darksky.net/forecast/'

    df = pd.read_csv('data/virus_data.csv')

    locations = list(df.location.unique())

    conn = sqlite3.connect('data/data.db')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS "environment";')

    create_environment_table_command = '''
    CREATE TABLE IF NOT EXISTS environment (
    	location VARCHAR(30) NOT NULL,
    	aqi INTEGER NOT NULL,
        temp REAL NOT NULL,
    	PRIMARY KEY (location)
    );
    '''

    c.execute(create_environment_table_command)

    conn.commit()

    for loc in range(len(locations)):

        if type(locations[loc]) == float:
            continue

        geocode_result = gmaps.geocode(locations[loc])

        if len(geocode_result) == 0:
            continue

        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']

        req = requests.get(URL_AQI+'geo:'+str(lat)+';'+str(lng)+'/?token='+TOKEN)
        res = req.json()

        req_weather = requests.get(URL_WEATHER+WEATHER_TOKEN+'/'+str(lat)+","+str(lng)+"?exclude="+exclude_weather)
        res_weather = req_weather.json()
        temp_min = res_weather['daily']['data'][0]['temperatureMin']
        temp_max = res_weather['daily']['data'][0]['temperatureMax']
        avg_temp = (temp_min + temp_max)/2.0

        if res['status'] == 'error' or res['status'] == 'nope':
            continue

        c.execute('''INSERT INTO environment VALUES (?, ?, ?);''', (locations[loc], res['data']['aqi'], avg_temp)) # insert into environment


    conn.commit()
    print('Environment table created!')

create_virus_table()
create_environment_table()
