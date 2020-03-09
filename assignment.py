from bs4 import BeautifulSoup
import requests
import sqlite3
import urllib
import xlrd
import os
import datetime

### IEX TRADING API METHODS ###
IEX_TRADING_URL = "https://cloud.iexapis.com/stable/stock/"


### YAHOO FINANCE SCRAPING
MOST_ACTIVE_STOCKS_URL = "https://cs.brown.edu/courses/csci1951-a/resources/stocks_scraping_2020.html"

### Register at IEX to receive your unique token
TOKEN = 'pk_962983467ea04c1ea01e9d3b9c159fa6'

# TODO: Use BeautifulSoup and requests to collect data required for the assignment.

stock_data = {}

# PART 1: Getting Data from 50 most active stocks
def get_stock_data():
    ''' PART 1: Web Scraping
        - Gets data from 50 most active stocks and saves to stock_data
    '''
    req = urllib.request.Request(MOST_ACTIVE_STOCKS_URL)
    response = urllib.request.urlopen(req)
    html_doc = response.read()
    html_dump = BeautifulSoup(html_doc, 'html.parser')

    # There is only one table body on the page (the 50 stocks)
    stock_table_rows = html_dump.find_all('tbody')[0].find_all('tr')

    # List of dicts that contain info about stock
    stock_info_list = {}

def get_coronavirus_data():
    file_path = 'data/coronavirus.xls'

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
        report_date = s.cell_value(i, 2)
        if len(str(report_date)) == 0:
            good_data = False
        data_entry["report_date"] = report_date

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
            if visiting == '1':
                data_entry["visiting_wuhan"] = True
            elif visiting == '0':
                data_entry["visiting_wuhan"] = False

        # 9. From Wuhan
        from_wuhan = str(s.cell_value(i, 16))
        if from_wuhan == 'NA' or from_wuhan == '':
            good_data = False
        else:
            if from_wuhan == '1':
                data_entry["from_wuhan"] = True
            elif from_wuhan == '0':
                data_entry["from_wuhan"] = False

        # 10. Death:
        death = str(s.cell_value(i, 17))
        if death == 'NA' or death == '':
            good_data = False
        else:
            if death == '1' or len(death) > 1:
                data_entry["death"] = True
            elif from_wuhan == '0':
                data_entry["death"] = False

        # Appends entry if it is valid data
        if good_data:
            data_list.append(data_entry)

    return data_list

# cv_data = get_coronavirus_data()

# TODO: Save data below.

# Create connection to database
conn = sqlite3.connect('../data/data.db')
c = conn.cursor()

# Delete tables if they exist
c.execute('DROP TABLE IF EXISTS "coronavirus";')
# c.execute('DROP TABLE IF EXISTS "quotes";')

#TODO: Create tables in the database and add data to it. REMEMBER TO COMMIT

create_coronavirus_table_command = '''
CREATE TABLE IF NOT EXISTS companies (
	id INT NOT NULL,
	report_date FLOAT NOT NULL,
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
#
# create_quotes_table_command = '''
# CREATE TABLE IF NOT EXISTS quotes (
# 	symbol VARCHAR(6) NOT NULL,
# 	price FLOAT NOT NULL,
#     avg_price FLOAT NOT NULL,
#     num_articles INT NOT NULL,
#     volume INT NOT NULL,
# 	change_pct FLOAT,
# 	PRIMARY KEY (symbol)
# );
# '''
#
# # Creates the companies and quotes tables
c.execute(create_coronavirus_table_command)

# Fills in tables with data from stock information
for i in get_coronavirus_data():
    # cur_data = stock_data[symb]
    # c.execute('''INSERT INTO companies VALUES (?, ?, ?);''', (symb, cur_data['name'], cur_data['hq']))
    c.execute('''INSERT INTO quotes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (i["id"], i["report_date"], i['summary'], i['city'], i['country'], i['gender'], i['age'], i['visiting_wuhan'], i['from_wuhan'], i['death']))

# Commits out changes to the database.
conn.commit()
