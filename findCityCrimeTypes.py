from pathlib import Path
import pandas as pd
from datetime import datetime
import os

directory = './StandardizedCityData'

files = Path(directory).glob('*')
newDataFrame = pd.DataFrame()
for file in files:
    print("Finding crime types in " + file.name)
    try:
        data = pd.read_csv(file)
        crimeTypes = data["offense"].unique()
        tempDataFrame = pd.DataFrame()
        tempDataFrame[file.name.split('_')[0]] = crimeTypes
        newDataFrame = pd.concat([newDataFrame, tempDataFrame], axis=1)
    except Exception as e:
        print("Unable to find crime types in " + file.name +
              ". This was the resulting error message: \n" + str(e))
        continue

newDataFrame.to_csv('./uniqueCrimeTypes.csv', index=False)
