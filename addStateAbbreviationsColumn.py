# The main goal of this script is to add a state column with correct state abbreviation to each city for each city data. The city data that needed State abbreviation must be generated before running this script. This script will got through each CityData csv file and check for State column, if it already exists we skip that file or else we will add that column to that csv file.
from pathlib import Path
import pandas as pd

# dictionary of state abbreviations for each city
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

# Path to CityData directory
directory = './CityData'

files = Path(directory).glob('*')
# Loop through all CityData files to add state abbreviation column
for file in files:
    data = pd.read_csv(file)
    # if state column already exists, skip file else add state column
    if "state" in data.columns:
        print("State column already exists for " + file.name)
        continue
    else:
        print("Adding state column for " + file.name)
        data["state"] = stateabbreviations[file.name.split("_")[0]]
        data.to_csv("./CityData/"+file.name, index=False)
    