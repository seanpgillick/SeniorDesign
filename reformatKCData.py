# Main goal of this script is to properlu assign lantitude and longitude to Kansas City Data. 

from cmath import isnan
import sys
import pandas as pd
from pathlib import Path
import ast
import os

path = Path("./CityData/Kansas City_data.csv")

# Must have Kansas City_data.csv in CityData folder
if (not path.is_file()):
    print("Unable to find Kansas City_data.csv. Run 'python ./retrieveSocrataApiData.py' to generate this file")
else:
    kc_df = pd.read_csv(path)
    # Iterate through each row to find proper lat and long
    for ind in kc_df.index:
        location = kc_df["latitude"][ind]
        # Condition for each date group
        if (kc_df["date"][ind] < '2021-01-01'):
            # Drop rows with missing latitude and longitude
            if (type(location) is float):
                continue
            else:
                dict_location = ast.literal_eval(location)
                kc_df.at[ind, "latitude"] = dict_location["latitude"]
                kc_df.at[ind, "longitude"] = dict_location["longitude"]
        else:
            if (type(location) is float):
                continue
            else:
                dict_location = ast.literal_eval(location)
                kc_df.at[ind, "latitude"] = dict_location["coordinates"][1]
                kc_df.at[ind, "longitude"] = dict_location["coordinates"][0]
    # Save new Kansas City_data.csv file
    os.remove("./CityData/Kansas City_data.csv")
    kc_df.to_csv('./CityData/Kansas City_data.csv', index=False)
