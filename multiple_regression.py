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

        with open(file_path) as jsonfile:
            data = json.load(jsonfile)
        data = pd.DataFrame.from_dict(data,orient='index')

        #choose variables
        data = data[variables + ['total_infections']].dropna()
        X = data[variables].to_numpy()
        y = data['total_infections'].to_numpy()

        return X, y


    # variables = ["government_effectiveness", "law_enforcement_ability", "corruption_level", "human_freedom"]
    variables = ["government_effectiveness", "stringency_index", "human_freedom"]

    # variables = ["max_infections"]
    X, y = load_file("infections.json", variables)

    # THRESHOLDS FOUND TO SEPARATE TESTING GROUPS INTO H/M/L
    LOW_THRESHOLD = 590
    HIGH_THRESHOLD = 6200

    # Dict where key is Testing Group LABEL, and value is list of indices representing data points
    data_groups = {}

    # Find the indices of data that belong in each testing group
    data_groups["LOW"] = np.argwhere(y<LOW_THRESHOLD).tolist()
    data_groups["MEDIUM"] = np.argwhere(np.logical_and(y>=LOW_THRESHOLD, y<=HIGH_THRESHOLD)).tolist()
    data_groups["HIGH"] = np.argwhere(y>HIGH_THRESHOLD).tolist()

    # Loops through each testing group to perform the regression:
    for label, indices_list in data_groups.items():

        # Indices list is plain list of numbers (had to do this because np.argwhere returns list of lists)
        indices = [item for sublist in indices_list for item in sublist]

        print('Current Testing Group: ' + label)
        print('Variables used: ' + ", ".join(variables))
        print('Number of countries: ' + str(len(indices)))

        cur_X = X[indices]
        cur_y = y[indices]

        cur_X = sm.add_constant(cur_X)

        model = sm.OLS(cur_y, cur_X)
        results = model.fit()

        mse = eval_measures.mse(cur_y, results.predict(cur_X))

        print(results.summary())
        print('R-squared = ' + str(results.rsquared))
        print('MSE = ' + str(mse))
        print("-----------------------------------------------")
