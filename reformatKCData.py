from cmath import isnan
import sys
import pandas as pd
from pathlib import Path
import ast
import os

path = Path("./CityData/Kansas City_data.csv")

if (not path.is_file()):
    print("Unable to find Kansas City_data.csv. Run 'python ./retrieveSocrataApiData.py' to generate this file")
else:
    kc_df = pd.read_csv(path)
    for ind in kc_df.index:
        location = kc_df["latitude"][ind]
        if (kc_df["date"][ind] < '2021-01-01'):
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
    os.remove("./CityData/Kansas City_data.csv")
    kc_df.to_csv('./CityData/Kansas City_data.csv', index=False)
