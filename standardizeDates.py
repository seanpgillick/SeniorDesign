# This script should loop through all the cities in CityData and reformat the date column to dd/mm/YYYY

from pathlib import Path
import pandas as pd
from datetime import datetime
import os

directory = './CityData'

files = Path(directory).glob('*')
for file in files:
    print("Reformatting dates in " + file.name)
    if file.name == "Washington D.C._data.csv" :
        try:
            data = pd.read_csv(file)
            data["0"] = pd.to_datetime(data["0"])
            data["0"] = data["0"].dt.strftime('%m/%d/%Y')
            os.remove("./CityData/"+file.name)
            data.to_csv("./CityData/"+file.name, index=False)
        except Exception as e:
            print("Unable to reformat dates in " + file.name +
                ". This was the resulting error message: \n" + str(e))
            continue
    else:
        try:
            data = pd.read_csv(file)
            data["date"] = pd.to_datetime(data["date"])
            data["date"] = data['date'].dt.strftime('%m/%d/%Y')
            os.remove("./CityData/"+file.name)
            data.to_csv("./CityData/"+file.name, index=False)
        except Exception as e:
            print("Unable to reformat dates in " + file.name +
                ". This was the resulting error message: \n" + str(e))
            continue
    
