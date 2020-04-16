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

"""
H_0: There is no association between Stringency Levels and Max infections in a day
H_a: There is an association between Stringency Levels and Max infections in a day
"""

# -------------------Chi Squared TEST -------------------------------

"""
H_0: There is no association between Freedom Levels and Number of Cases
H_a: There is an association between Freedom Levels and Number of Cases
"""


def load_file(file_path):
    """input: file_path: the path to the data file
        output: X: array of independent variables values, y: array of the dependent variable values
    """

    #set up data from json
    with open(file_path) as jsonfile:
        data = json.load(jsonfile)
    data = pd.DataFrame.from_dict(data,orient='index')

    #choose variables
    variables = ['human_freedom','total_infections','max_infections','total_tests','StringencyIndex']
    data = data[variables] 

    #see min max
    # print(data.min())
    # print(data.max())

    #convert freedom_index into category
    """
    4-5, 5-6, 6-7, 7-8, 7-9
    """
    freedom_category = []
    for value in data['human_freedom'].values:
        if value < 5.0:
            freedom_category.append('Low')
        elif value < 6.0:
            freedom_category.append('Low-Med')
        elif value < 7.0:
            freedom_category.append('Med')
        elif value < 8.0:
            freedom_category.append('Med-High')
        else:
            freedom_category.append('High')
    data['freedom_level'] = freedom_category

    #convert stringency_index into category
    # """
    # 40-60, 60-80, 80-100
    # """
    # percentile1 = np.nanpercentile(data['StringencyIndex'].values,30)
    # print(percentile1)
    # percentile2 = np.nanpercentile(data['StringencyIndex'].values,70)
    # print(percentile2)

    stringency_level = []
    for value in data['StringencyIndex'].values:
        if value < 71.906:
            stringency_level.append('Low')
        elif value < 95.00:
            stringency_level.append('Med')
        elif value < 101.0:
            stringency_level.append('High')
        else:
            stringency_level.append("None")
    
    data['stringency_level'] = stringency_level
        
    return data

def add_testing_group(data): 
    testing = np.array(data['total_tests'])
    testing = testing.reshape(-1, 1)
    testing = np.log(testing)

    kmeans = KMeans(n_clusters = 3).fit(testing)

    cats = [None, None, None]
    cluster_centers = kmeans.cluster_centers_
    cats[np.argmin(cluster_centers)] = "Low"
    cats[np.argmax(cluster_centers)] = "High"
    for s in range(3):
        if cats[s] == None:
            cats[s] = "Medium"

    labels = [cats[i] for i in kmeans.labels_]

    groups = []
    labels = kmeans.labels_


    for j in range(len(labels)):
        groups.append(cats[labels[j]])
    
    data['testing_group'] = groups

    return data

def get_controlled_data(data):
    df1 = data[data['testing_group'] == "Low"]
    df2 = data[data['testing_group'] == "Medium"]
    df3 = data[data['testing_group'] == "High"]

    return [("Low",df1),("Medium",df2),("High",df3)]


def set_up_observed(data,freedom_level):

    cross_table = pd.crosstab(data["freedom_level"], data["infection_level"], margins=True)
    cross_table = cross_table[["Low","Low-Med","Med-High","High"]]
    cross_table = cross_table.reindex(freedom_level)
    observed = cross_table
    observed.columns = list(cross_table.columns) # Set columns names
    observed.index = freedom_level
    return observed


def set_up_observed_stringency(data,stringency_level,infection_level):

    cross_table = pd.crosstab(data["stringency_level"], data["infection_level"], margins=True)
    cross_table = cross_table[infection_level]
    cross_table = cross_table.reindex(stringency_level)
    observed = cross_table
    observed.columns = list(cross_table.columns) # Set columns names
    observed.index = stringency_level
    return observed
    


def conduct_test(observed_data):
    chi_squared, p_value, degrees_of_freedom, expected = stats.chi2_contingency(observed=observed_data)
    print(f"chi_squared={chi_squared}, p_value={p_value}, degrees_of_freedom={degrees_of_freedom}")

"""
To find groups for infections
"""
def get_infections_groups(data):

    infections = np.array(data['total_infections'])
    infections = infections.reshape(-1, 1)
    inertia = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters = i).fit(infections)
        inertia.append(kmeans.inertia_)
    inertia_data = [[i for i in range(1,11)], inertia]

    #inertia to find ideal number of clusters
    fig = px.line(inertia_data, x = inertia_data[0], y = inertia_data[1])
    # fig.show()


    kmeans = KMeans(n_clusters = 4).fit(infections)
    
    countries = list(data.index.values)

    k_means_data = [countries, kmeans.labels_, data['total_infections']]
    fig = px.scatter(k_means_data, x = k_means_data[0], y = k_means_data[2], log_y = True, color = k_means_data[1])
    fig.update_traces(textposition='top center')
    # fig.show()


    categories = [None, None, None, None]
    cluster_centers = kmeans.cluster_centers_
    cluster_copy = kmeans.cluster_centers_.copy()
    cluster_copy = sorted(cluster_copy)
    index = []

    for i in range(4):
        for j in range(4):
            if cluster_copy[i] == cluster_centers[j]:
                index.append(i)


    categories[index[0]] = "Low"
    categories[index[1]] = "Low-Med"
    categories[index[2]] = "Med-High"
    categories[index[3]] = "High"
    
    
    labels = [categories[i] for i in kmeans.labels_]
    data['infection_level'] = labels

    return data




    

if __name__=='__main__':


    """
    H_0: There is no association between Freedom Levels and Number of Cases
    H_a: There is an association between Freedom Levels and Number of Cases
    """

    """
    Chi Square Test for Freedom Index without controlling for testing
    """
    data = load_file("infections.json")
    data = get_infections_groups(data)


    # print("Testing for Freedom Level")
    # observed = set_up_observed(data,["Low","Low-Med","Med","Med-High","High"])
    # conduct_test(observed)


    # # #Chi Square Test for Freedom Index with controlling for testing

    # #Get Testing Groups
    data = add_testing_group(data)
    data_groups = get_controlled_data(data)
    # #print(data_groups)

  
    # #Test group low testing
    # data = data_groups[0][1]
    # data = get_infections_groups(data)
    # observed = set_up_observed(data,["Low","Low-Med","Med","Med-High"])
    # conduct_test(observed)

    # #Test group medium testing
    # data = data_groups[1][1]
    # data = get_infections_groups(data)
    # observed = set_up_observed(data,["Low","Low-Med","Med","Med-High","High"])
    # conduct_test(observed)

    # #Test group high testing
    # data = data_groups[2][1]
    # data = get_infections_groups(data)
    # observed = set_up_observed(data,["Low-Med","Med","Med-High","High"])
    # conduct_test(observed)
    
 
    # data = get_infections_groups(data)
    # print("Testing for Stringency Level")
    # observed = set_up_observed_stringency(data,["Low","Med","High"],["Low","Low-Med","Med-High","High"])
    # print(observed)
    # conduct_test(observed)

    #Chi Square Test for Stringency with controlling for testing

    # #Test group low testing
    print("Testing for Stringency Level: Low Testing Group")
    data = data_groups[0][1]
    data = get_infections_groups(data)
    observed = set_up_observed_stringency(data,["Low","Med","High"],["Low","Low-Med","Med-High","High"])
    conduct_test(observed)

    #Test group medium testing
    print("Testing for Strigency Level: Medium Testing Group")
    data = data_groups[1][1]
    data = get_infections_groups(data)
    observed = set_up_observed_stringency(data,["Low","Med","High"],["Low","Low-Med","Med-High","High"])
    conduct_test(observed)

    # #Test group high testing
    print("Testing for Strigency Level: High Testing Group")
    data = data_groups[2][1]
    data = get_infections_groups(data)
    observed = set_up_observed_stringency(data,["Low","Med","High"],["Low","Low-Med","Med-High","High"])
    print(observed)
    conduct_test(observed)
    

 
    



