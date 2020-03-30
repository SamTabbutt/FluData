# FluData
Using Google flu data to visualize the geographic trends of the spread of virus

The flu data is particularly fascinating to watch as a seemingly-chaotic pattern emerges both spatially and temporily.

I used the publically accessible [Google flu trends data](https://www.google.org/flutrends/about/) and processed it with pandas and matplotlib to create a modular data pipeline for visualizing data in the format output from Google flu trends. Here is an example which collects data from three separate files (Canada, US, and Mexico), and visualizes it in one subplot matrix. 

![alt-text](https://github.com/SamTabbutt/FluData/blob/master/Vis.gif)

## Using the python files
### DataScrape 

   function:

   Open Google Flu Trends .csv file
   
   Reorganize data with geographic coordinates tied to each data point
   
   Save 2 formats of data as <file_name>FullLinear.csv and <file_name>Full.csv
   
Parameters:

   [1]: Name of .csv file in <working_dir>/raw_data directory
   
   [2]: The name of the first city listed in the .csv file. 
   
   IF param [2] == 'Global': first layer is labeled 'Global' and every other layer is labeled 'Nation'
   
Example:

      python DataScrape.py US Anchorage
 Will create two structured .csv files including location longitude and latitude
   
### DataVis

DataVis: to visualize a 2-d-spatial/temporal map of Google Flu Trends

Input: Processed data from Google Flu Trends with latitude and longitude tied to each location

Output: animated 2x2 plot with four plots--

   Plot 1,1: bar chart of 'frequency of flu searches' x 'latitude of search location'
   
   Plot 1,2: lineplot of 'total frequency of flue searches' x 'date'
   
   Plot 2,1: heat map of x='latitude of search' x y='longitude of search' x color='frequency of flue searches'
   
   Plot 2,2: bar chart of 'longitude of search location' x 'frequency of flu searches'
   
   Time component: Along time axis, current date of data displayed in Plot 1,2
   
Parameters: 

   [1]: Names of files to pull from <working_dir>/refined_data
   
   If intended to compile from multiple files: <name_1>/<name_2>
       
   If intended to pull from one file: <name>
       
   [2]: Boolean for save/display. 
   
   If intending to save animation: T
       
   If intending to show animation: F
       
   Example calls from terminal: 
   
       python DataVis.py US/World/Australia F
       
   Will gather data compiled from 'US', 'World', and 'Australia' and show the plot
           
       python DataVis.py US T
       
   Will gather data compiled from 'US', andsave the animation as .mp4
           
Normalization:

   Given the scale inconsistancies between different Google Flu Trends files, the data is normalized with respect
   to the results of each file. 

