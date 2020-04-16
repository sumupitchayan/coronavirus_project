import numpy as np
import pandas as pd
import geopandas as gpd
import random
from shapely.geometry import Point
import csv
import matplotlib.pyplot as plt
import plotly.graph_objects as go
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




    ## PLOT MAP 1 of GOVERNMENT EFFECTIVENESS against TOTAL INFECTIONS 
    # plot layer 1
    
    fig = go.Figure(data=go.Choropleth(
        locations=df['iso_a3'], # Spatial coordinates
        z = df['government_effectiveness'].astype(float), # Data to be color-coded
        locationmode = 'ISO-3', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Government Effectiveness",
    ))
    df.dropna( inplace=True)
    print(df)
    # plot layer 2
    scale = 30
    # infections = df[['iso_a3', 'lat', 'long', 'max_infections']].to_numpy()
    # print(infections)
    # fig.add_trace(go.Scattergeo(
    #     locationmode = 'ISO-3',
    #     lon = df['long'],
    #     lat = df['lat'],
    #     text = df['iso_a3'],
    #     marker = dict(
    #         size = df['total_infections']/scale,
    #         color = 'blue',
    #         opacity=0.4,
    #         line_color='rgb(40,40,40)',
    #         # color='rgba(102, 102, 102)',
    #         line_width=0.5,
    #         sizemode='area'
    #     ),
    #     name="total infection per million"
    # )
    # )
    fig.update_layout(
        # title_text = 'Worldwide Coronavirus Total Infection per M and government effectiveness',
        title_text = 'Map of Government effectiveness',
        showlegend = True,
        geo = dict(
            landcolor = 'rgb(217, 217, 217)',
        )
    )
    fig.show()




    ## PLOT MAP 2 of STRINGENCY INDEX against TOTAL INFECTIONS 
    # plot layer 1

    fig = go.Figure(data=go.Choropleth(
        locations=df['iso_a3'], # Spatial coordinates
        z = df['stringency_index'].astype(float), # Data to be color-coded
        locationmode = 'ISO-3', # set of locations match entries in `locations`
        colorscale = 'Blues',
        colorbar_title = "Stringency Index",
    ))
    df.dropna( inplace=True)
    print(df)
    # plot layer 2
    # fig.add_trace(go.Scattergeo(
    #     locationmode = 'ISO-3',
    #     lon = df['long'],
    #     lat = df['lat'],
    #     text = df['iso_a3'],
    #     marker = dict(
    #         size = df['total_infections']/scale,
    #         color = 'red',
    #         opacity=0.4,
    #         line_color='rgb(40,40,40)',
    #         # color='rgba(102, 102, 102)',
    #         line_width=0.5,
    #         sizemode='area'
    #     ),
    #     name="total infection rate"
    # )
    # )
    fig.update_layout(
        title_text = 'Map of Stringency Index',
        showlegend = True,
        geo = dict(
            
            landcolor = 'rgb(217, 217, 217)',
        )
    )
    fig.show()




    
    fig = go.Figure(data=go.Choropleth(
        locations=df['iso_a3'], # Spatial coordinates
        z = df['total_infections'].astype(float), # Data to be color-coded
        locationmode = 'ISO-3', # set of locations match entries in `locations`
        colorscale = 'Greens',
        colorbar_title = "Government Effectiveness",
    ))
    df.dropna( inplace=True)
    print(df)
    # plot layer 2
    scale = 30
    # infections = df[['iso_a3', 'lat', 'long', 'max_infections']].to_numpy()
    # print(infections)
    # fig.add_trace(go.Scattergeo(
    #     locationmode = 'ISO-3',
    #     lon = df['long'],
    #     lat = df['lat'],
    #     text = df['iso_a3'],
    #     marker = dict(
    #         size = df['total_infections']/scale,
    #         color = 'blue',
    #         opacity=0.4,
    #         line_color='rgb(40,40,40)',
    #         # color='rgba(102, 102, 102)',
    #         line_width=0.5,
    #         sizemode='area'
    #     ),
    #     name="total infection per million"
    # )
    # )
    fig.update_layout(
        title_text = 'Map of Total Infection per 1M ',
        showlegend = True,
        geo = dict(
            landcolor = 'rgb(217, 217, 217)',
        )
    )
    fig.show()
    # ## PLOT MAP 3 of STRINGENCY INDEX and TOTAL INFECTIONS
    # # plot layer 1
    # z = df.stringency_index * df.total_infections

    # fig = go.Figure(data=go.Choropleth(
    #     locations=df['iso_a3'], # Spatial coordinates
    #     z = z.astype(float), # Data to be color-coded
    #     locationmode = 'ISO-3', # set of locations match entries in `locations`
    #     colorscale = 'Blues',
    #     colorbar_title = "Total Infection per M x Stringency Index",
    # ))

    # df.dropna( inplace=True)
    # fig.update_layout(
    #     title_text = 'Worldwide Coronavirus Total Infection per M x Stringency Index per country',
    #     showlegend = True,
    #     geo = dict(
            
    #         landcolor = 'rgb(217, 217, 217)',
    #     )
    # ) 
    # fig.show()


    # ## PLOT MAP 4 of GOVERNMENT EFFECTIVENESS and TOTAL INFECTIONS

    # z = df.government_effectiveness * df.total_infections

    # fig = go.Figure(data=go.Choropleth(
    #     locations=df['iso_a3'], # Spatial coordinates
    #     z = z.astype(float), # Data to be color-coded
    #     locationmode = 'ISO-3', # set of locations match entries in `locations`
    #     colorscale = 'Reds',
    #     colorbar_title = "Total Infection per M x Government Effectiveness",
    # ))

    # df.dropna( inplace=True)
    # fig.update_layout(
    #     title_text = 'Worldwide Coronavirus Total Infection per M x Government Effectiveness per country',
    #     showlegend = True,
    #     geo = dict(
            
    #         landcolor = 'rgb(217, 217, 217)',
    #     )
    # ) 
    # fig.show()



