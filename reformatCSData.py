# Main goal of this script is to properly assign lantitude and longitude to Colorado Springs Data. 

from cmath import isnan
import sys
import pandas as pd
from pathlib import Path
import ast
import os

path = Path("./CityData/Colorado Springs_data.csv")

# Must have Colorado Springs_data.csv in CityData folder
if (not path.is_file()):
    print("Unable to find Colorado Springs_data.csv. Run 'python ./retrieveSocrataApiData.py' to generate this file")
else:
    cs_df = pd.read_csv(path)
    # Iterate through each row to find proper lat and long
    for ind in cs_df.index:
        location = cs_df["latitude"][ind]
        # Condition for each date group
        if (cs_df["date"][ind] < '2021-01-01'):
            # Drop rows with missing latitude and longitude
            if (type(location) is float):
                continue
            else:
                dict_location = ast.literal_eval(location)
                cs_df.at[ind, "latitude"] = dict_location["coordinates"][1]
                cs_df.at[ind, "longitude"] = dict_location["coordinates"][0]
        else:
            if (type(location) is float):
                continue
            else:
                dict_location = ast.literal_eval(location)
                cs_df.at[ind, "latitude"] = dict_location["coordinates"][1]
                cs_df.at[ind, "longitude"] = dict_location["coordinates"][0]
    # Save new Colorado Springs_data.csv file
    os.remove("./CityData/Colorado Springs_data.csv")
    cs_df.to_csv('./CityData/Colorado Springs_data.csv', index=False)
