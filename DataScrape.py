#DataScrape function:
#   Open Google Flu Trends .csv file
#   Reorganize data with geographic coordinates tied to each data point
#   Save 2 formats of data as <file_name>FullLinear.csv and <file_name>Full.csv
#Parameters:
#   [1]: Name of .csv file in <working_dir>/raw_data directory
#   [2]: The name of the first city listed in the .csv file. 
#   IF param [2] == 'Global': first layer is labeled 'Global' and every other layer is labeled 'Nation'


#imports
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import googlemaps
import os
import sys

#define working directory constant
working_dir = os.path.dirname(os.path.realpath(__file__))

#grab first parameter as .csv name
file_name = sys.argv[1]
fluPATH = os.path.join(working_dir,'raw_data',file_name+'.csv')

#Create automatic dataframe from .csv
fluData = pd.read_csv(fluPATH)
#Set date as index
fluData = fluData.set_index('Date')

#Interpolate all missing data points along time axis
fluData.interpolate(axis=1)

#Grab the name of the first city listed to categorize scale of each data layer
Nation_first_city_name = sys.argv[2]

#Reorder the dataset to query date/location result
locationFrames = []
#Initialize first layer as 'Nation'
Layer_set = 'Nation'
if file_name == 'World':
    Layer_set = 'State'

#For each column in fluData:
for (i,col) in enumerate(fluData.columns):
    #Create empty data frame
    col_df = pd.DataFrame()
    #Copy date list over to empty frame
    col_df['Date'] = fluData.index
    #Set date as index
    col_df = col_df.set_index('Date')
    #Copy location for each row of new dataframe
    col_df['Location'] = col
    #Copy results over to column dataframe
    col_df['Results'] = fluData[col]
    #Use geocoder for retreival of laditude/longitude data for location
    locator = Nominatim(user_agent="myGeocoder")
    location = locator.geocode(col)
    #Auto-update layer label
    if i == 1 and file_name!='World':
        Layer_set = 'State'
    if 'HHS' in col:
        Layer_set = 'Region'
    if col == Nation_first_city_name:
        Layer_set = 'City'
    col_df['Layer'] = Layer_set
    #If the geocoder knows the region: append full column to locationFrames
    try:
        col_df['Latitude'] = location.latitude
        col_df['Longitude'] = location.longitude
        col_df['Results'] = col_df['Results'].fillna(0)
        locationFrames.append(col_df)
        #Print to console for confirmation:
        print(i,col_df)
    #Else: skip column
    except:
        print("Location not valid")

#Save full dataframes to <working_dir>/refined_data
full_df = pd.concat(locationFrames,axis=1)
full_df.to_csv(os.path.join('refined_data',file_name+'Full.csv'))
full_df_lin = pd.concat(locationFrames)
full_df_lin.to_csv(os.path.join('refined_data',file_name+'FullLinear.csv'))
