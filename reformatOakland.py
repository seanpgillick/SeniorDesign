from cmath import isnan
import sys
import pandas as pd
from pathlib import Path
import ast
import os

path = Path("./CityData/Oakland_data.csv")

if (not path.is_file()):
    print("Unable to find Oakland_data.csv. Run 'python ./retrieveSocrataApiData.py' to generate this file")
else:
    print("Reformatting location data for Oakland...")
    o_df = pd.read_csv(path)
    # Iterate through each row to find proper lat and long
    for ind in o_df.index:
        location = o_df["latitude"][ind]
        # If it is a dictionary, extract it
        if (type(location) is str):
            dict_location = ast.literal_eval(location)
            o_df.at[ind, "latitude"] = dict_location["coordinates"][1]
            o_df.at[ind, "longitude"] = dict_location["coordinates"][0]
              
    # Save new Auburn_data.csv file
    os.remove("./CityData/Oakland_data.csv")
    o_df.to_csv('./CityData/Oakland_data.csv', index=False)