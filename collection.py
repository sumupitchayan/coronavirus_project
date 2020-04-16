import pandas as pd
import sqlite3
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import plotly.express as px
import math
import csv

print("Running..")
df = pd.read_csv("data/time_series_covid19_confirmed_global.csv")


countries = df["Country/Region"].unique()
infections = {}

for c in range(len(countries)):
    vals = df[df["Country/Region"] == countries[c]].values
    matrix = np.array(vals)[:, 4:]
    total = np.sum(matrix, axis = 0)
    country = countries[c]
    if country == "Korea, South":
        country = "South Korea"
    if country == "Taiwan*":
        country = "Taiwan"
    if country == "Czechia":
        country = "Czech Republic"

# added long & lat
    infections[country] = {"total_infections": np.sum(total), "max_infections": np.max(total), "lat":float(np.array(vals)[:,2][0]), "long":float(np.array(vals)[:,3][0])}
    infections[country]['stringency_index'] = None
    
    

aliases = {  # value is name of country in database/ key is name that may be from other sources
    "USA": "US",
    "S. Korea": "South Korea",
    "UK": "United Kingdom",
    "Burma": "Myanmar",
    "United States": "US",
    "Russian Federation": "Russia",
    "Lao PDR": "Laos",
    "UAE": "United Arab Emirates",
    "Brunei Darussalam": "Brunei",
    "Korea, Rep.": "South Korea",
    "Korea, South": "South Korea",
    "Dominican Rep.": "Dominican Republic",
    "Czechia": "Czech Republic",
    "Czech Republic (Czechia)": "Czech Republic",
    "Czech Rep.": "Czech Republic",
    "Saint Kitts & Nevis": "Saint Kitts and Nevis",
    "Congo, Rep. Of": "Congo (Brazzaville)",
    "Congo, Dem. R.": "Congo (Kinshasa)",
    "C?te d'Ivoire": "Cote d'Ivoire",
    "Gambia, The":"Gambia",
    "Pap. New Guinea":"Papua New Guinea",
    "Myanmar":"Burma",
    "Taiwan, China":"Taiwan",
    "Egypt, Arab Rep.":"Egypt",
    "Iran, Islamic Rep.": "Iran",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Macedonia, FYR":"North Macedonia",
    "Slovak Republic": "Slovakia",
    "Venezuela, RB":"Venezuela",
    "Democratic Republic of Congo": "Congo (Kinshasa)",
    "Sao Tome & Principe": "Sao Tome and Principe"
    }

res = requests.get("https://www.worldometers.info/world-population/population-by-country/")  #scraping population
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.find("table").find_all("tr")

for row in items[1:]:
    information = row.find_all('td')
    country = information[1].text.strip()
    pop = information[2]
    age = information[9].text.strip()
    info = ''.join(pop.text.strip().split(","))
    if country in aliases:
        country = aliases[country]
    if not info or country not in infections:
        continue
    infections[country]['population'] = int(info)
    infections[country]['max_infections'] = (infections[country]['max_infections']/int(info))*1000000
    infections[country]['total_infections'] = (infections[country]['total_infections']/int(info))*1000000
    if age != "N.A.":
        infections[country]['median_age'] = int(age.strip())

infections['Liechtenstein']['median_age'] = float(43.4) #sourced from UN indicators
infections['Dominica']['median_age'] = float(34) #sourced from UN indicators


res = requests.get("https://www.worldometers.info/coronavirus/")  #scraping testing
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.find("table").find_all("tr")


for row in items[1:]:
    information = row.find_all('td')
    country = information[0].text.strip()
    test = information[10]
    info = ''.join(test.text.strip().split(","))
    if country in aliases:
        country = aliases[country]
    if not info or country not in infections:
        continue

    infections[country]['total_tests'] = (int(info)/infections[country]['population'])*1000000

df = pd.read_csv("data/gov_effect.csv")
for row in df.values:
    country = row[0]

    if country in aliases:
        country = aliases[country]

    if country not in infections or row[1] != row[1]:
        continue

    infections[country]['government_effectiveness'] = float(row[1])
    infections[country]['law_enforcement_ability'] = float(row[2])
    infections[country]['corruption_level'] = float(row[3])

df = pd.read_csv("data/hfi_cc_2019.csv")

for row in df.values:
    country = row[2]

    if country in aliases:
        country = aliases[country]

    if country not in infections or row[4] =='-':
        continue

    infections[country]['human_freedom'] = float(row[4])

# Government health expenditure as % of GDP -- latest numbers are from 2016:
df = pd.read_csv("data/gov_healthexp_pct_gdp.csv")

for row in df.values:
    country = row[0]

    if country in aliases:
        country = aliases[country]

    if country not in infections or row[1] != row[1]:
        continue
    infections[country]['iso_a3'] = row[1]
    infections[country]['gov_healthexp_pct_gdp'] = float(row[60])

# Government health expenditure per capita (in USD) -- latest numbers are from 2016:
df = pd.read_csv("data/gov_healthexp_percap.csv")
for row in df.values:
    country = row[0]

    if country in aliases:
        country = aliases[country]

    if country not in infections or row[1] != row[1]:
        continue

    infections[country]['gov_healthexp_per_capita'] = float(row[60])


# Government lockdown measures
df = pd.read_csv("data/gov_lockdown_v2.csv")
date = 20200405
df = df.loc[df['Date'] == date]
df = df[['CountryName', 'StringencyIndexForDisplay'
    ]]

# ['CountryName', 'S1_School closing', 'S2_Workplace closing', 'S3_Cancel public events', 'S4_Close public transport', 'S5_Public information campaigns', \
#     'S6_Restrictions on internal movement', 'S7_International travel controls', 'S8_Fiscal measures', 'S9_Monetary measures', 'S10_Emergency investment in health care' , 'S11_Investment in Vaccines', 'S12_Testing framework', 'S13_Contact tracing', 'StringencyIndex'
#     ]

# print(df)
for row in df.values:
    country = row[0]

    if country in aliases:
        country = aliases[country]

    # print(country)
    # print(df.columns)
    if country in infections:
       columns = df.columns
       for i in range(len(columns)):
            if columns[i] == 'CountryName':
               continue
            if columns[i] == 'StringencyIndexForDisplay' and float(row[i]) > 100.0:
                continue
            
            infections[country]['stringency_index'] = float(row[i])





# print(len(infections)) #181 here
removed_countries = []
countries_without_freedom = []
keys = list(infections.keys())  # data cleaning - remove countries with no population/median age/gov_effect/testing estimate
# print(keys)
for i in range(len(keys)):
    if 'human_freedom' not in infections[keys[i]]:
        countries_without_freedom.append(keys[i])

    # added for government lockdown measures
    # for j in range(len(search_keywords)):
    #     if search_keywords[j] not in infections[keys[i]]:
    #         infections[keys[i]][search_keywords[j]] = None


    if len(list(infections[keys[i]].keys())) != 15:
        removed_countries.append(keys[i])
        del infections[keys[i]]

# print(infections)
# print(len(infections)) # 122 here - lot of countries have missing testing data
with open('infections.json', 'w') as outfile:
    json.dump(infections, outfile, indent=4, sort_keys=True)


# Creates CSV file: infections.csv ----------
country_list = list(infections.keys())
with open('infections.csv', 'w', newline='') as f:
    writer = csv.writer(f)

    # Writes header
    header = ['country'] + list(infections[country_list[0]].keys())
    writer.writerow(header)

    # Adds each row
    for country in country_list:
        row = [country] + (list(infections[country].values()))
        writer.writerow(row)


# # ---------------------GRAPHING---------------------------

# print("Graphing..")
# data = [list(infections.keys()), [infections[k]["total_infections"] for k in infections], [infections[k]["total_tests"] for k in infections]]
# fig = px.scatter(data, x = data[1], y = data[2], text = data[0], log_x = True, log_y = True, color = [infections[k]["government_effectiveness"] for k in infections])
# fig.update_traces(textposition='top center')
# fig.show()


# plot for government control
# print("Graphing..")
# data = [list(infections.keys()), [infections[k]["total_infections"] for k in infections], [infections[k]["stringency_index"] for k in infections]]
# fig = px.scatter(data, x = data[1], y = data[2], text = data[0], log_x = True, log_y = False)
# fig.update_traces(textposition='top center')
# fig.show()
