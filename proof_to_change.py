import pandas as pd
import sqlite3
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import plotly.express as px
import math
import plotly.offline as offline


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
    infections[country] = {"total_infections": np.sum(total), "max_infections": np.max(total)}

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
    "Sao Tome & Principe":"Sao Tome and Principe"



    }
df = df.drop(["Province/State","Lat","Long"],axis=1)
data_columns = list(df.columns)
China = []
Other_Countries = []

for row in df.values:
    if row[0] == "China":
        China = row
    else:
        Other_Countries.append(row)

Other_Countries = np.sum(np.array(Other_Countries),axis=0)
Other_Countries[0] = "Other Countries"

data = np.vstack((data_columns,China, Other_Countries))
data = data.transpose()
data = data[1:]


data = pd.DataFrame(data, columns=["Date","China","Other Countries"])
data.drop(0)
# data['China'][0] = np.log(data['China'][0])
# print(data['China'][0])
data['China'] = data['China'].astype(str).astype(int)
data['Other Countries'] = data['Other Countries'].astype(str).astype(int)
data['log_China'] = np.log(data['China'])
data['log_Other_Countries'] = np.log(data['Other Countries'])



df_melt = pd.melt(data,id_vars='Date', value_vars=["China", "Other Countries"])

fig = px.line(df_melt, x='Date' , y='value' , color='variable')
fig.update_layout(title="Infections Over Time",legend_title='<b> Country </b>',yaxis_title="log of infections per 1million",width=1000,
    height=600)
fig.add_shape(
        # Line Vertical
        dict(
            type="line",
            x0='3/13/20',
            y0=-100000,
            x1='3/13/20',
            y1=2100000,
            line=dict(
                color="LightGreen",
                width=3
            )))
    
fig.show()





df_melt = pd.melt(data,id_vars='Date', value_vars=["log_China", "log_Other_Countries"])

fig = px.line(df_melt, x='Date' , y='value' , color='variable')
fig.update_layout(title="Log of Infections Over Time",legend_title='<b> Country (log) </b>',yaxis_title="log of infections per 1million",width=1000,
    height=600)
fig.add_shape(
        # Line Vertical
        dict(
            type="line",
            x0='3/13/20',
            y0=0,
            x1='3/13/20',
            y1=16,
            line=dict(
                color="LightGreen",
                width=3
            )))
    
fig.show()
