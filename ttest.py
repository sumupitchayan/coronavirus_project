import pandas as pd
import sqlite3
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import plotly.express as px
import math
import csv
import scipy.stats as stats
from sklearn.cluster import KMeans


# -------------------T TEST -------------------------------
def manual_t_test_ind(a, b):
  n_a = np.shape(a)[0]
  n_b = np.shape(b)[0]
  t = (np.mean(a) - np.mean(b)) / (np.sqrt((np.var(a))/n_a + (np.var(b))/n_b))
  return t

def degrees_of_freedom(a, b):
  s_1 = np.var(a)
  s_2 = np.var(b)
  n_1 = np.shape(a)[0]
  n_2 = np.shape(b)[0]

  nr = ((s_1/n_1) + (s_2/n_2))**2
  dr = (((s_1/n_1)**2)/(n_1 - 1)) + (((s_2/n_2)**2)/(n_2 - 1))
  return nr / dr


def conduct_t_test(group, measure, infections, threshold):

    high = []
    low = []
    x = []

    for country in group:
        if infections[country][measure]:
            x.append(infections[country][measure])

    low_cut = np.percentile(np.array(x), 30)
    high_cut = np.percentile(np.array(x), 70)

    for country in group:
        if infections[country][measure] == None:
            continue
        if infections[country][measure] > high_cut:
            high.append(infections[country]['total_infections'])
        if infections[country][measure] < low_cut:
            low.append(infections[country]['total_infections'])

    # Null - S_low - S_high = 0
    # Alternative - S_low - S_high > 0
    # alpha = 0.05

    t_stat = manual_t_test_ind(np.array(low), np.array(high))
    degree = len(high) + len(low) - 2
    print("degrees of freedom - " + str(degree))
    # degree = degrees_of_freedom(np.array(high), np.array(low))
    print("T-stat -- " + str(t_stat))
    crit = stats.t.ppf(0.95, degree)
    print("T-Crit -- " + str(crit))

    if t_stat > crit:
        print("Reject Null")

    else:
        print("Do not reject Null")

    print("\n")



# # ---------------------KMEANS---------------------------

with open('infections.json', 'r') as f:
    infections = json.load(f)

testing = np.array([infections[k]['total_tests'] for k in infections]).reshape(-1,1)
testing = np.log(testing)
inertia = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters = i).fit(testing)
    inertia.append(kmeans.inertia_)
data = [[i for i in range(1,11)], inertia]

# fig = px.line(data, x = data[0], y = data[1])
# fig.show()


kmeans = KMeans(n_clusters = 3).fit(testing)

data = [list(infections.keys()), kmeans.labels_, [infections[k]["total_tests"] for k in infections]]
fig = px.scatter(data, x = data[0], y = data[2], log_y = True, color = data[1])
fig.update_traces(textposition='top center')
fig.show()

# ---------------------------END OF KMEANS----------------------------------


tot_infections = [infections[k]["total_infections"] for k in infections]
countries = list(infections.keys())
government_effectiveness = [infections[k]["stringency_index"] for k in infections]

cats = [None, None, None]
cluster_centers = kmeans.cluster_centers_
cats[np.argmin(cluster_centers)] = "Low"
cats[np.argmax(cluster_centers)] = "High"
for s in range(3):
    if cats[s] == None:
        cats[s] = "Medium"

labels = [cats[i] for i in kmeans.labels_]


data = [countries, tot_infections ,labels , government_effectiveness]
fig = px.scatter(data, x = data[1], y = data[3], hover_name = data[0], log_x = True, log_y = False, color = data[2])
fig.update_traces(textposition='top center')
fig.update_layout(legend_title='<b> Testing </b>')


fig.update_layout(
    title="Effect of Stringency Index on Coronavirus Infections",
    xaxis_title="Total Infections per 1M",
    yaxis_title="Stringency Index",
)

fig.show()

# ----- T Test -----

# First split into groups by testing using results of KMeans

groups = {}
labels = kmeans.labels_
keys = list(infections.keys())

for i in range(3):
    g = []
    for j in range(len(labels)):
        if labels[j] == i:
            g.append(keys[j])
    groups[cats[i]] = g


# Countries with lower stringency index have more total infections than countries with higher stringency index
# Countries with lower government effectiveness index have more total infections than countries with higher stringency index
# Same with human Freedom

# first tried with threshold - then median - then only top 20 and bottom 20%


measures = [["stringency_index", 60], ["government_effectiveness", 0], ["human_freedom", 0]]

for m in measures:
    for k in groups:
        print("Measure = " + str(m[0]))
        print("Group = " + str(k))

        conduct_t_test(groups[k], m[0], infections, m[1])
