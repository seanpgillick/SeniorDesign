# This script is used to find unique crime types in each city and store the unique Crime Types to ./uniqueCrimeTypes.csv file

from pathlib import Path
import pandas as pd
from datetime import datetime
import os

directory = './StandardizedCityData'

files = Path(directory).glob('*')
newDataFrame = pd.DataFrame()

# Iterate through each file in directory and find unique crime types
for file in files:
    print("Finding crime types in " + file.name)
    try:
        data = pd.read_csv(file)
        crimeTypes = data["offense"].unique()
        tempDataFrame = pd.DataFrame()
        tempDataFrame[file.name.split('_')[0]] = crimeTypes
        #Concatenate temp dataframe to new dataframe
        newDataFrame = pd.concat([newDataFrame, tempDataFrame], axis=1)
    # Error handling
    except Exception as e:
        print("Unable to find crime types in " + file.name +
              ". This was the resulting error message: \n" + str(e))
        continue

# Save unique crime types to ./uniqueCrimeTypes.csv file
newDataFrame.to_csv('./uniqueCrimeTypes.csv', index=False)
