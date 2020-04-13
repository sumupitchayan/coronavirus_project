import numpy as np
import pandas as pd
import random
import csv
from scipy import stats
import statsmodels.api as sm
from statsmodels.tools import eval_measures
import json

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
    def load_file(file_path):
        """input: file_path: the path to the data file
           output: X: array of independent variables values, y: array of the dependent variable values
        """
        #TODO:
        #1. Use pandas to load data from the file. Here you can also re-use most of the code from part I.
        #2. Select which independent variables best predict the dependent variable count.
        df = pd.read_csv(file_path, keep_default_na=True, na_filter=True)
        y = df['total_infections'].tolist()

        print(df.columns)
        variables = ['gov_healthexp_per_capita']
        # variables.remove('StringencyIndex')
        # variables.remove('gov_healthexp_per_capita')

        X = df[variables].to_numpy()

        pd.set_option("display.max_rows", None, "display.max_columns", None)

        return X, y

    X, y = load_file("infections.csv")

    ##################################################################################
    # TODO: use train test split to split data into x_train, x_test, y_train, y_test #
    #################################################################################

    # x_train, x_test, y_train, y_test = train_test_split(X, y, p)

    ##################################################################################
    # TODO: Use StatsModels to create the Linear Model and Output R-squared
    #################################################################################

    # x_train = sm.add_constant(x_train)
    # x_test = sm.add_constant(x_test)
    X = sm.add_constant(X)

    # model = sm.OLS(y_train, x_train)
    model = sm.OLS(y, X)
    results = model.fit()

    # Prints out the Report
    # TODO: print R-squared, test MSE & train MSE

    print(results.summary())
    # r_sq = results.rsquared
    # train_mse = eval_measures.mse(y_train, results.predict(x_train))
    # test_mse = eval_measures.mse(y_test, results.predict(x_test))
    #
    # print('Training R-squared: ' + str(r_sq))
    # print('Training MSE: ' + str(train_mse))
    # print('Testing MSE: ' + str(test_mse))
