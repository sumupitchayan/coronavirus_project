import numpy as np
import pandas as pd
import random
import csv
from scipy import stats
import statsmodels.api as sm
from statsmodels.tools import eval_measures
import json
from sklearn.cluster import KMeans

def split_data(data, prob):
    """input:
	 data: a list of pairs of x,y values
	 prob: the fraction of the dataset that will be testing data, typically prob=0.2
	 output:
	 two lists with training data pairs and testing data pairs
	"""
    #TODO: Split data into fractions [prob, 1 - prob]. You can re-use the code from part I.
    split_index = int(len(data[0]) * (1 - prob))
    X = data[0]
    y = data[1]

    zipped = zip(X, y)
    pairs = list(zipped)
    random.shuffle(pairs)

    train = []
    test = []

    for i in range(0, len(pairs)):
        if i > split_index:
            test.append(pairs[i])
        else:
            train.append(pairs[i])
    return train, test

def train_test_split(x, y, test_pct):
	"""input:
	x: list of x values, y: list of independent values, test_pct: percentage of the data that is testing data=0.2.

	output: x_train, x_test, y_train, y_test lists
	"""

	#TODO: Split the features X and the labels y into x_train, x_test and y_train, y_test as specified by test_pct.
	#You can re-use code from part I.
	train, test = split_data((x, y), test_pct)

	x_train = [pair[0] for pair in train]
	x_test = [pair[0] for pair in test]
	y_train = [pair[1] for pair in train]
	y_test = [pair[1] for pair in test]

	return x_train, x_test, y_train, y_test

if __name__=='__main__':

    # DO not change this seed. It guarantees that all students perform the same train and test split
    random.seed(1)
    # Setting p to 0.2 allows for a 80% training and 20% test split
    p = 0.2

    def get_kmeans_labels():
        """ output: returns labels ("High", "Medium", "Low") representing each country's testing levels
        """
        with open('infections.json', 'r') as f:
            infections = json.load(f)

        testing = np.array([infections[k]['total_tests'] for k in infections]).reshape(-1,1)
        testing = np.log(testing)
        inertia = []
        for i in range(1, 11):
            kmeans = KMeans(n_clusters = i).fit(testing)
            inertia.append(kmeans.inertia_)
        data = [[i for i in range(1,11)], inertia]

        kmeans = KMeans(n_clusters = 3).fit(testing)

        # data = [list(infections.keys()), kmeans.labels_, [infections[k]["total_tests"] for k in infections]]
        # fig = px.scatter(data, x = data[0], y = data[2], log_y = True, color = data[1])
        # fig.update_traces(textposition='top center')
        # fig.show()

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
        label_names = labels

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

        return kmeans.labels_, label_names

    #############################################
    # TODO: open csv and read data into X and y #
    #############################################
    def load_file(file_path, variables):
        """input: file_path: the path to the data file
           output: X: array of independent variables values, y: array of the dependent variable values
        """
        #TODO:
        #1. Use pandas to load data from the file. Here you can also re-use most of the code from part I.
        #2. Select which independent variables best predict the dependent variable count.

        with open('infections.json', 'r') as f:
            infections = json.load(f)

        columns = {}
        countries_list = list(infections.keys())
        metric_names = list(infections[countries_list[0]].keys())
        for metric in metric_names:
            for country in countries_list:
                if metric not in columns.keys():
                    columns[metric] = [infections[country][metric]]
                else:
                    columns[metric] += [infections[country][metric]]
            columns[metric] = np.asarray(columns[metric])

        x_cols = []
        for var in variables:
            x_cols.append(columns[var])
        X = np.column_stack(x_cols)

        y = columns["total_infections"]

        return X, y



    variables = ["government_effectiveness", "law_enforcement_ability", "corruption_level", "human_freedom"]
    # variables = ["max_infections"]
    X, y = load_file("infections.json", variables)

    labels, label_names = get_kmeans_labels()
    # print(testing_labels)

    for i in range(4):

        indices = []


        # Finds indices for current group (H/L/M)
        for j in range(0, len(labels)):
            if labels[j] == i:
                indices.append(j)

        cur_group = "ALL"

        # Performs on all groups
        if i == 3:
            indices = range(len(labels))
        else:
            cur_group = label_names[indices[0]]

        print('Current Testing Group: ' + cur_group)
        print('Variables used: ' + ", ".join(variables))
        print('Number of countries: ' + str(len(indices)))

        cur_X = X[indices]
        cur_y = y[indices]

        cur_X = sm.add_constant(cur_X)

        model = sm.OLS(cur_y, cur_X)
        results = model.fit()

        mse = eval_measures.mse(cur_y, results.predict(cur_X))

        # print(results.summary())
        print('R-squared = ' + str(results.rsquared))
        print('MSE = ' + str(mse))
        print("-----------------------------------------------")
