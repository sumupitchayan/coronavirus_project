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
    variables = ['country', 'iso_a3','lat','long','total_infections','max_infections','stringency_index', 'government_effectiveness']

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
    df = X.merge(world, on='iso_a3', how="right")
    print(world)

    # plot layer 1
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Choropleth(
        locations=df['iso_a3'], # Spatial coordinates
        z = df['government_effectiveness'].astype(float), # Data to be color-coded
        locationmode = 'ISO-3', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "government effectiveness",
    ))
    df.dropna( inplace=True)
    print(df)
    # plot layer 2
    scale = 2
    # infections = df[['iso_a3', 'lat', 'long', 'max_infections']].to_numpy()
    # print(infections)
    fig.add_trace(go.Scattergeo(
        locationmode = 'ISO-3',
        lon = df['long'],
        lat = df['lat'],
        text = df['iso_a3'],
        marker = dict(
            size = df['max_infections']/scale,
            color = 'blue',
            opacity=0.4,
            line_color='rgb(40,40,40)',
            # color='rgba(102, 102, 102)',
            line_width=0.5,
            sizemode='area'
        ),
        name="max infection rate"
        # colorbar_title = "max infection rate",
    )
    )
    # for i in range(len(infections)):
    #     countryname = infections[i,0]
    #     lat_ = infections[i,1]
    #     long_ = infections[i,2]
    #     max_infections = infections[i, 3]

    fig.update_layout(
        title_text = 'Worldwide Coronavirus total infection rates and government effectiveness',
        showlegend = True,
        geo = dict(
            
            landcolor = 'rgb(217, 217, 217)',
        )
    )

    fig.show()



    # fig, ax = plt.subplots(figsize = (8,3)) 
    
    # # 
    # # world.plot(column='stringency_index', ax=ax,edgecolor='k', legend=True, missing_kwds={'color': 'lightgrey'}, cmap='Blues')
    # # plt.show()
    # world.plot(column='government_effectiveness', ax=ax,edgecolor='k', legend=True, missing_kwds={'color': 'lightgrey'},cmap='OrRd')
    # # world.plot(column='StringencyIndex', ax=ax,edgecolor='k')


    # plt.show()
