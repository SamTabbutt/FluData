#DataVis: to visualize a 2-d-spatial/temporal map of Google Flu Trends
#Input: Processed data from Google Flu Trends with latitude and longitude tied to each location
#Output: animated 2x2 plot with four plots--
#   Plot 1,1: bar chart of 'frequency of flu searches' x 'latitude of search location'
#   Plot 1,2: lineplot of 'total frequency of flue searches' x 'date'
#   Plot 2,1: heat map of x='latitude of search' x y='longitude of search' x color='frequency of flue searches'
#   Plot 2,2: bar chart of 'longitude of search location' x 'frequency of flu searches'
#   Time component: Along time axis, current date of data displayed in Plot 1,2
#Parameters: 
#   [1]: Names of files to pull from <working_dir>/refined_data
#       If intended to compile from multiple files: <name_1>/<name_2>
#       If intended to pull from one file: <name>
#   [2]: Boolean for save/display. 
#       If intending to save animation: T
#       If intending to show animation: F
#   Example calls from terminal: 
#       python DataVis.py US/World/Australia F
#           Will gather data compiled from 'US', 'World', and 'Australia' and show the plot
#       python DataVis.py US T
#           Will gather data compiled from 'US', andsave the animation as .mp4
#Normalization:
#   Given the scale inconsistancies between different Google Flu Trends files, the data is normalized with respect
#   to the results of each file. 

import numpy as np
import pandas as pd
import os
import sys
import matplotlib

#Call for save_visualization parameter and setup matplotlib to save if True
save = sys.argv[2]
if save=='T':
    matplotlib.use("Agg")
from matplotlib import pyplot as plt
import seaborn as sns
import matplotlib.animation as animation

#Define working_dir parameter
working_dir = os.path.dirname(os.path.realpath(__file__))

#Call for file_name parameter and save path as fluPATH
file_names = sys.argv[1]
fileList = []
for f in file_names.split('/'):
    fileList.append(os.path.join(working_dir,'refined_data',f+'Full.csv'))

#Define interest columns for display
interestCols = ['Location','Results','Latitude','Longitude','Layer']

#Define function to call specific column names for groupings of a location's data
#The data is saved from DataScrape.py along the same axis for all locations within a file
#To get the column names for associated groupings call grabLocationGroupDict(colName)
def grabLocationGroupDict(colName):
    nationName = colName.split('_')[0]
    if len(colName.split('.'))==1:
        colIndex = ''
    else:
        colIndex = '.'+colName.split('.')[1]
    locDict = {c:nationName+'_'+c+colIndex for c in interestCols}
    return locDict

#Create pd dataframe from refined_csv file for each filename listed
fluDataSets = []
for i,f in enumerate(fileList):
    fluData = pd.read_csv(f)
    newCols = []
    #Rename columns in a data frame to be associated with the file they came from
    #Avoids repeated column names when pulling from multiple files
    for col in fluData.columns:
        #Date is consistant along axis=1
        if col != 'Date':
            newCols.append(file_names.split('/')[i]+"_"+col)
        else:
            newCols.append('Date')
    fluData.columns = newCols
    fluData = fluData.set_index('Date')
    for col in fluData.columns:
        #For now, drop all locations with Layer: 'Region','City'
        if 'Layer' in col:
            if fluData[col].value_counts().index[0] in ['Region','City']:
                locDict = grabLocationGroupDict(col)
                for l in locDict:
                    fluData = fluData.drop(locDict[l],axis=1)
    #Normalize along all 'Results' columns
    numCols = []
    for col in fluData.columns:
        if 'Results' in col:
            numCols.append(col)
    column_maxes = fluData[numCols].max()
    df_max = column_maxes.max()
    fluData[numCols] = fluData[numCols] / df_max
    #Append dataSet to fluDataSets
    fluDataSets.append(fluData)

#Join all the loaded data frames
fluData = pd.concat(fluDataSets,axis=1,join='outer',sort=True)
results_cols = []
for col in fluData.columns:
    if 'Results' in col:
        results_cols.append(col)
        #Interpolate missing values in between known values
        fluData[col] = fluData[col].interpolate()
        #Fill all remaining Nan with 0
        fluData[col] = fluData[col].fillna(0)

#Define fill column with mode function
def fillColNaWithMode(col):
    if 'Results' in col.name:
        return col
    col.fillna(col.value_counts().index[0], inplace=True)
    return col

#Fill all remaining missing values with the mode of the associated column
fluData = fluData.apply(lambda col:fillColNaWithMode(col))

#Create column in fluData that is the total of all Results associated with Layer 'Nation'
#Drop all column groups with Layer = 'Nation'
nationFrame = pd.DataFrame()
nationFrame['Date'] = fluData.index
nationFrame = nationFrame.set_index('Date')
for col in fluData.columns:
    if 'Layer' in col:
        layerDict = grabLocationGroupDict(col)
        if fluData[layerDict['Layer']].value_counts().index[0]=='Nation':
            nationFrame[layerDict['Results']] = fluData[layerDict['Results']]
            for col in layerDict:
                fluData = fluData.drop(layerDict[col],axis=1)

nationFrame['Total'] = 0
for col in nationFrame.columns:
    if col!='Total':
        nationFrame['Total'] = nationFrame['Total'] + nationFrame[col]
fluData['Total'] = nationFrame['Total']

#Swap dataFrame axis to respresent all groupings in the vertical axis
dateFrame = pd.DataFrame(columns = interestCols)
for col in fluData.columns:
    if 'Location' in col:
        locDict = grabLocationGroupDict(col)
        locRow = pd.DataFrame()
        for i,l in enumerate(locDict):
            locRow[interestCols[i]] = fluData[locDict[l]]
        dateFrame = dateFrame.append(locRow)

#Group by date and append each date group to animation data
AnimationData = []
dateFrame['Date'] = dateFrame.index
sortedDateFrame = dateFrame.groupby('Date')
for date in sortedDateFrame:
    AnimationData.append(date[1])

#Define a function to return a heatmap based on latitude longitude and frequency
def setHeatMapMatrix(lon,lat,results):
    resultMatrix = np.zeros(shape=(120,150))
    margin = (max(lat)-min(lat))/10
    latScale = np.linspace(min(lat)-margin,max(lat)+margin,num=120)
    longScale = np.linspace(min(lon)-margin,max(lon)+margin,num=150)
    lateFine = (latScale[1]-latScale[0])*3
    longFine = (longScale[1]-longScale[0])*3
    for k,s in enumerate(lon):
        points = (np.where(abs(longScale-s)<longFine),np.where(abs(latScale-lat.iloc[k])<lateFine))
        for point in points[0][0]:
            for point2 in points[1][0]:
                if k<len(results.iloc[:]):
                    resultMatrix[119-point2][point] = results.iloc[k]
    return resultMatrix

#Set up plot
fig,axs = plt.subplots(2,2)
longitudes = AnimationData[-1]['Longitude']
latitudes = AnimationData[-1]['Latitude']
bar = axs[0][0].bar(x = longitudes, height = AnimationData[-1]['Results'])
barh = axs[1][1].barh(y = latitudes, width = AnimationData[-1]['Results'])

heatData = setHeatMapMatrix(longitudes, latitudes, AnimationData[-1]['Results'])
latScale = np.linspace(min(latitudes)-1,max(latitudes)+1,num=10)
for i,n in enumerate(latScale):
    latScale[i] = round(n)
longScale = np.linspace(min(longitudes)-1,max(longitudes)+1,num=10)
for i,n in enumerate(longScale):
    longScale[i] = round(n)
hist = axs[1][0].imshow(heatData,vmax=1)

linePlot = axs[0][1].plot(fluData.index,fluData['Total'])
line = axs[0][1].axvline(x=fluData.index[0])
txt = axs[0][1].text(2,max(fluData['Total'])*5/6,"")
axs[0][1].set_xticklabels([])
axs[0][1].set_yticklabels([])
axs[0][1].set_xticks([])

axs[1][0].set_xticklabels(longScale)
axs[1][0].set_yticklabels(latScale)
axs[1][0].set_xlabel('Latitude')
axs[1][0].set_ylabel('Longitude')
axs[0][0].set_xticklabels([])
axs[0][0].tick_params(axis='y',labelrotation=90,labelsize=5)
axs[0][0].set_ylabel('Flu Search Frequency')
axs[1][1].set_xlabel('Flu Search Frequency')
axs[1][1].set_yticklabels([])
plots = [bar,barh,hist,txt,line]
fig.tight_layout(pad=0)

fig.suptitle('Google Flu Data for '+file_names)

#Define animation function.
def update_long_plot(i):
    for j,bar in enumerate(plots[0]):
        if j<len(AnimationData[i]['Results'].iloc[:]):
            bar.set_height(AnimationData[i]['Results'].iloc[j])
            bar.set_color((AnimationData[i]['Results'].iloc[j]/25000,.5,.5,1))
        else:
            bar.set_height(0)
    for j,bar in enumerate(plots[1]):
        if j<len(AnimationData[i]['Results'].iloc[:]):
            bar.set_width(AnimationData[i]['Results'].iloc[j])
            bar.set_color((AnimationData[i]['Results'].iloc[j]/25000,.5,.5,1))
        else:
            bar.set_height(0)
    if axs[0][0].get_ylim()[1]<AnimationData[i]['Results'].max():
        axs[0][0].set_ylim(0,AnimationData[i]['Results'].max())
        axs[1][1].set_xlim(0,AnimationData[i]['Results'].max())
    heatData = setHeatMapMatrix(longitudes, latitudes, AnimationData[i]['Results'])
    plots[2].set_data(heatData)
    plots[3].set_text(fluData.index[i])
    plots[4].set_xdata(fluData.index[i])
    return plots

#Run animation
longAni = animation.FuncAnimation(
    fig, update_long_plot, interval=3, blit=False, save_count=5000,repeat=False)

#Save animation as .mp4 if save parameter is true
if save == 'T':
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    longAni.save('im.mp4', writer=writer)
#Else, show animation
else:
    plt.show()