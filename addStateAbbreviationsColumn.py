from pathlib import Path
import pandas as pd


stateabbreviations = {
    "Atlanta": "GA",
    "Auburn": "WA",
    "Austin": "TX",
    "Baltimore": "MD",
    "Boston": "MA",
    "Buffalo": "NY",
    "Chicago": "IL",
    "Cincinnati": "OH",
    "Colorado Springs": "CO",
    "Fort Worth": "TX",
    "Gainesville": "GA",
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
    "Oakland": "CA",
    "Omaha": "NE",
    "Philadelphia": "PA",
    "Portland": "OR",
    "Raleigh": "NC",
    "San Francisco": "CA",
    "Seattle": "WA",
    "Washington D.C.": "DC",
}

directory = './CityData'

files = Path(directory).glob('*')
# Loop through all CityData files to add state abbreviation column
for file in files:
    data = pd.read_csv(file)
    data["state"] = stateabbreviations[file.name.split("_")[0]]
    data.to_csv("./CityData/"+file.name, index=False)
    