import numpy as np
import pandas as pd
import geopandas as gpd
import random
from shapely.geometry import Point
import csv
import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
# import mpl_toolkits


def load_file(file_path):
    """input: file_path: the path to the data file
        output: X: array of independent variables values, y: array of the dependent variable values
    """
    df = pd.read_csv(file_path, keep_default_na=True, na_filter=True)
    print(df.columns)
    variables = ['country', 'iso_a3','lat','long','total_infections','max_infections','StringencyIndex']

    df = df[variables]
    df["coordinates"] = list(zip(pd.to_numeric(df.long), pd.to_numeric(df.lat)))

    df["coordinates"] = df["coordinates"].apply(Point)
    return df


if __name__=='__main__':

    X= load_file("infections.csv")

    # convert to geodf
    X = gpd.GeoDataFrame(X)

    # prepare polygons
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    world = X.merge(world, on='iso_a3', how="right")
    print(world)

    fig, ax = plt.subplots(figsize = (8,3)) 
    
    
    world.plot(column='StringencyIndex', ax=ax,edgecolor='k', legend=True, missing_kwds={'color': 'lightgrey'}, cmap='Blues')
    # plt.show()
    # world.plot(column='StringencyIndex', ax=ax,edgecolor='k', legend=True, missing_kwds={'color': 'lightgrey'},cmap='OrRd')
    # world.plot(column='StringencyIndex', ax=ax,edgecolor='k')


    plt.show()
