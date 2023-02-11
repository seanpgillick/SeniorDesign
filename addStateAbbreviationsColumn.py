from pathlib import Path
import pandas as pd


stateabbreviations = {
    "Atlanta": "GA",
    "Austin": "TX",
    "Baltimore": "MD",
    "Boston": "MA",
    "Buffalo": "NY",
    "Chicago": "IL",
    "Cincinnati": "OH",
    "Colorado Springs": "CO",
    "Fort Worth": "TX",
    "Houston": "TX",
    "Kansas City": "MO",
    "Los Angeles": "CA",
    "Memphis": "TN",
    "Mesa": "AZ",
    "Milwaukee": "WI",
    "Minneapolis": "MN",
    "Montgomery": "AL",
    "Nashville": "TN",
    "New York": "NY",
    "Omaha": "NE",
    "Philadelphia": "PA",
    "Portland": "OR",
    "Raleigh": "NC",
    "San Francisco": "CA",
    "Seattle": "WA",
    "Washington D.C.": "DC",
}

directory = './CityData'
# file = 'Demo_data.csv'

files = Path(directory).glob('*')
# Loop through all CityData files reformat the date column to dd/mm/YYYY
for file in files:
    data = pd.read_csv(file)
    data["state"] = stateabbreviations[file.name.split("_")[0]]
    data.to_csv("./CityData/"+file.name, index=False)
        # data.insert(0, column = "state", value = stateabbreviations[file.name.split("_")[0]])
        # print(stateabbreviations[file.name.split("_")[0]])
    # print("Reformatting dates in " + file.name.split("_")[0])

# data = pd.read_csv(directory)
# data["state"] = stateabbreviations[file.name.split("_")[0]]

# print(stateabbreviations["Atlanta"])
