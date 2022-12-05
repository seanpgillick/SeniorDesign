# This script should loop through all the cities in CityData and reformat the date column to dd/mm/YYYY

from pathlib import Path
import pandas as pd
from datetime import datetime
import os

directory = './CityData'

files = Path(directory).glob('*')
#Loop through all CityData files reformat the date column to dd/mm/YYYY
for file in files:
    print("Reformatting dates in " + file.name)
    #Specific if condition to handle Washington D.C data
    if file.name == "Washington D.C._data.csv" :
        try:
            data = pd.read_csv(file)
            data["0"] = pd.to_datetime(data["0"])
            data["0"] = data["0"].dt.strftime('%m/%d/%Y')
            #Removing old unformated file and adding new csv file with reformated date
            os.remove("./CityData/"+file.name)
            data.to_csv("./CityData/"+file.name, index=False)
        #Error handling
        except Exception as e:
            print("Unable to reformat dates in " + file.name +
                ". This was the resulting error message: \n" + str(e))
            continue
    #condition for other city datas
    else:
        try:
            data = pd.read_csv(file)
            data["date"] = pd.to_datetime(data["date"])
            data["date"] = data['date'].dt.strftime('%m/%d/%Y')
            #Removing old unformated file and adding new csv file with reformated date
            os.remove("./CityData/"+file.name)
            data.to_csv("./CityData/"+file.name, index=False)
        #Error handling
        except Exception as e:
            print("Unable to reformat dates in " + file.name +
                ". This was the resulting error message: \n" + str(e))
            continue
    
