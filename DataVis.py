from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import os
import sys
import matplotlib

#Call for save_visualization parameter and setup matplotlib to save if True
save = sys.argv[2]
if save=='T':
    print('trying')
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
    fileList.append(os.path.join(working_dir,'refined_data',f+'FullLinear.csv'))

#Create default pd dataframe from refined_csv file for each filename listed
fluDataSets = []
for f in fileList:
    fluData = pd.read_csv(f)
    fluDataSets.append(fluData)

#Join all the loaded data frames
fluData = pd.concat(fluDataSets)

#Filter the State-labeled rows for visualization
stateData = fluData[fluData['Layer']=='State']

#Gather a summation of all nation data into dataframe
nationData = fluData[fluData['Layer']=='Nation']
nationSets = []
for i in nationData['Location'].unique():
    newSet = nationData[nationData['Location']==i]
    newSet.set_index('Date')
    nationSets.append(newSet)
fullData = pd.DataFrame()
fullData['Date'] = nationSets[0]['Date']
fullData['Results'] = nationSets[0]['Results']
for nation in nationSets:
    fullData['Results'] += nation['Results']

#Group state data by date for visualization
stateData_by_date = stateData.groupby('Date')

AnimationData = []
for Datedata in stateData_by_date:
    outside = Datedata[1][Datedata[1]['Location'].isin(['Alaska','Hawaii'])].index
    df = Datedata[1].drop(outside).copy()
    AnimationData.append(df)

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
                resultMatrix[119-point2][point] = results.iloc[k]
    return resultMatrix

fig,axs = plt.subplots(2,2)
longitudes = AnimationData[0]['Longitude']
latitudes = AnimationData[0]['Latitude']
bar = axs[0][0].bar(x = longitudes, height = AnimationData[0]['Results'])
barh = axs[1][1].barh(y = latitudes, width = AnimationData[0]['Results'])

heatData = setHeatMapMatrix(longitudes, latitudes, AnimationData[0]['Results'])
latScale = np.linspace(min(latitudes)-1,max(latitudes)+1,num=10)
for i,n in enumerate(latScale):
    latScale[i] = round(n)
longScale = np.linspace(min(longitudes)-1,max(longitudes)+1,num=10)
for i,n in enumerate(longScale):
    longScale[i] = round(n)
hist = axs[1][0].imshow(heatData,vmax=max(fullData['Results'])*2/4)

linePlot = axs[0][1].plot(fullData['Date'],fullData['Results'])
line = axs[0][1].axvline(x=fullData['Date'].iloc[0])
txt = axs[0][1].text(2,max(fullData['Results'])*5/6,"")
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

def update_long_plot(i):
    for j,bar in enumerate(plots[0]):
        bar.set_height(AnimationData[i]['Results'].iloc[j])
        bar.set_color((AnimationData[i]['Results'].iloc[j]/25000,.5,.5,1))
    for j,bar in enumerate(plots[1]):
        bar.set_width(AnimationData[i]['Results'].iloc[j])
        bar.set_color((AnimationData[i]['Results'].iloc[j]/25000,.5,.5,1))
    if axs[0][0].get_ylim()[1]<AnimationData[i]['Results'].max()+50:
        axs[0][0].set_ylim(0,AnimationData[i]['Results'].max()+50)
        axs[1][1].set_xlim(0,AnimationData[i]['Results'].max()+50)
    heatData = setHeatMapMatrix(longitudes, latitudes, AnimationData[i]['Results'])
    plots[2].set_data(heatData)
    plots[3].set_text(AnimationData[i]['Date'].iloc[0])
    plots[4].set_xdata(AnimationData[i]['Date'].iloc[0])
    return plots

longAni = animation.FuncAnimation(
    fig, update_long_plot, interval=1, blit=False, save_count=5000,repeat=False)

if save == 'T':
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    longAni.save('im.mp4', writer=writer)

else:
    plt.show()