from operator import truediv
from select import select
import sys
import pandas as pd
from sodapy import Socrata
import datetime
from pathlib import Path

# This dictionary stores socrata API information
# If your city uses socrata you can add it's information to this dictionary 
# dateCol --> The cities date column title
# offCol --> The cities offense column title
# latCol --> The cities latitude column title
# lonCol --> The cities longitue column title

cityApiInfo = {
    "New York": {
            "url":"data.cityofnewyork.us",
            "dateCol":"cmplnt_fr_dt",
            "offCol":"ofns_desc",
            "latCol":"latitude",
            "lonCol":"longitude",
            "keys":["qgea-i56i"]
        },
    "Los Angeles": {
            "url":"data.lacity.org",
            "dateCol":"date_occ",
            "offCol":"crm_cd_desc",
            "latCol":"lat",
            "lonCol":"lon",
            "keys":["63jg-8b9z","2nrs-mtv8"]
        },
    "Chicago": {
            "url":"data.cityofchicago.org",
            "dateCol":"date",
            "offCol":"primary_type",
            "latCol":"latitude",
            "lonCol":"longitude",
            "keys":["ijzp-q8t2"]
        },
}


def retrieveCityData(city, url, dateCol, offCol, latCol, lonCol, keys):
    csvName = city + "_data.csv"


    # Unauthenticated client only works with public data sets. Note 'None'
    # in place of application token, and no username or password:
    client = Socrata(url, None, timeout=120)

    # Example authenticated client (needed for non-public datasets):
    # client = Socrata(data.cityofnewyork.us,
    #                  MyAppToken,
    #                  userame="user@example.com",
    #                  password="AFakePassword")

    final_df = pd.DataFrame()
    selectString = dateCol+" as date,"+offCol+" as offense,"+latCol+" as latitude,"+lonCol+" as longitude"
    whereString = dateCol + " >= '2019-01-01' and " + dateCol + " < '2022-01-01'" 

    # Loop through the cities different endpoints
    for key in keys:
        looping = True
        offset = 0
        
        # Retrieve city data 2000 rows at a time
        while looping:
            results = client.get(key, limit=2000, offset=offset, where=whereString, select=selectString, order=dateCol)
            # Convert to pandas DataFrame
            results_df = pd.DataFrame.from_records(results)
            final_df = pd.concat([final_df, results_df])

            # If we have reached the end of the data, stop looping 
            # Else increase the offset and continue
            if (results_df.shape[0] < 2000):
                looping = False
            else:
                # print(results_df["date"].iloc[1999])
                offset += 2000
        
    final_df.to_csv('./CityData/'+csvName)

# Loop through the city api dictionary, retrieve the required data and export it to a csv
# If a csv file for a city already exists, it will be skipped
for city in cityApiInfo:
    csvName = city + "_data.csv"
    path = Path('./CityData/'+csvName)

    print("\nGathering Data for " + city)

    if(path.is_file()):
        print("Csv for " + city + " already exists. To regather this data, you must delete the following file: /CityData/" + city + "_data.csv")
    else:
        retrieveCityData(city, cityApiInfo[city]["url"], cityApiInfo[city]["dateCol"], cityApiInfo[city]["offCol"], cityApiInfo[city]["latCol"], 
        cityApiInfo[city]["lonCol"], cityApiInfo[city]["keys"]) 

