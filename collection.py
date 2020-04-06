import pandas as pd
import sqlite3
import numpy as np
import requests
from bs4 import BeautifulSoup
import json

df = pd.read_csv("time_series_covid19_confirmed_global.csv")

countries = df["Country/Region"].unique()
infections = {}

for c in range(len(countries)):
    vals = df[df["Country/Region"] == countries[c]].values
    matrix = np.array(vals)[:, 4:]
    total = np.sum(matrix, axis = 0)
    infections[countries[c]] = {"total_infections": np.sum(total), "max_infections": np.max(total)}

res = requests.get("https://www.worldometers.info/world-population/population-by-country/")  #scraping population
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.find("table").find_all("tr")

for row in items[1:]:
    information = row.find_all('td')
    country = information[1].text.strip()
    pop = information[2]
    age = information[9].text.strip()
    info = ''.join(pop.text.strip().split(","))
    if not info or country not in infections:
        continue
    infections[country]['population'] = int(info)
    infections[country]['max_infections'] /= int(info)
    infections[country]['total_infections'] /= int(info)
    if age != "N.A.":
        infections[country]['median_age'] = int(age.strip())

keys = list(infections.keys())  # data cleaning - remove countries with no population/median age estimate
for i in range(len(keys)):
    if len(list(infections[keys[i]].keys())) != 4:
        del infections[keys[i]]

with open('infections.json', 'w') as outfile:
    json.dump(infections, outfile, indent=4, sort_keys=True)