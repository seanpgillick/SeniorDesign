from cmath import isnan
import sys
import pandas as pd
from pathlib import Path
import ast
import os

path = Path("./CityData/Auburn_data.csv")

if (not path.is_file()):
    print("Unable to find Kansas City_data.csv. Run 'python ./retrieveSocrataApiData.py' to generate this file")
else:
    print("Reformatting location data for Auburn...")
    a_df = pd.read_csv(path)
    # Iterate through each row to find proper lat and long
    for ind in a_df.index:
        location = a_df["latitude"][ind]
        # If it is a dictionary, extract it
        if (type(location) is str):
            dict_location = ast.literal_eval(location)
            if("latitude" in dict_location):
                a_df.at[ind, "latitude"] = dict_location["latitude"]
                a_df.at[ind, "longitude"] = dict_location["longitude"]
            else:
                a_df.at[ind, "latitude"] = ""
                a_df.at[ind, "longitude"] = ""     

    # Save new Auburn_data.csv file
    os.remove("./CityData/Auburn_data.csv")
    a_df.to_csv('./CityData/Auburn_data.csv', index=False)

