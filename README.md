# FluData
Using Google flu data to visualize the geographic trends of the spread of virus

The flu data is particularly fascinating to watch as a seemingly-chaotic pattern emerges both spatially and temporily.

I used the publically accessible [Google flu trends data](https://www.google.org/flutrends/about/) and processed it with pandas and matplotlib to create a modular data pipeline for visualizing data in the format output from Google flu trends. Here is an example which collects data from three separate files (Canada, US, and Mexico), and visualizes it in one subplot matrix. 

![alt-text](https://github.com/SamTabbutt/FluData/blob/master/Vis.gif)

# Using the python files
DataScrape function:
   Open Google Flu Trends .csv file
   Reorganize data with geographic coordinates tied to each data point
   Save 2 formats of data as <file_name>FullLinear.csv and <file_name>Full.csv
Parameters:
   [1]: Name of .csv file in <working_dir>/raw_data directory
   [2]: The name of the first city listed in the .csv file. 
   IF param [2] == 'Global': first layer is labeled 'Global' and every other layer is labeled 'Nation'
