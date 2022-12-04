import json
from pathlib import Path
import requests
import pandas as pd
import datetime as dt


cityApiInfo = {
    "Washington D.C.": {
        "url": "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer/2/query?where=1%3D1&outFields=OFFENSE,LATITUDE,LONGITUDE,REPORT_DAT&outSR=4326&f=json",
    }
}

def retrieveCityData(city, url):
    csvName = city + "_data.csv"
    final_df = pd.DataFrame()
    looping = True
    offset = 0
    # Retrieve city data 2000 rows at a time
    while looping:
        results = requests.get(url)
        data = results.json()
        listDict = list(data.values())
        print(type(listDict[5][0]))
        alteredList = []
        for x in listDict[5]:
            tempList = []
            unixTime = x["attributes"]["REPORT_DAT"]/1000
            standardTime = dt.datetime.fromtimestamp(unixTime)
            tempList.append(standardTime)
            tempList.append(x["attributes"]["OFFENSE"])
            tempList.append(x["attributes"]["LATITUDE"])
            tempList.append(x["attributes"]["LONGITUDE"])
            alteredList.append(tempList)


        results_df = pd.DataFrame.from_dict(alteredList)
        results_df.columns = ['date','offense','latitude','longitude']
        final_df = pd.concat([final_df, results_df])

        # If we have reached the end of the data, stop looping
        # Else increase the offset and continue
        if (results_df.shape[0] < 2000):
            looping = False
        else:
            # print(results_df["date"].iloc[1999])
                offset += 2000

    final_df.to_csv('./CityData/'+csvName)


for city in cityApiInfo:
    csvName = city + "_data.csv"
    path = Path('./CityData/'+csvName)

    print("\nGathering Data for " + city)

    if (path.is_file()):
        print("Csv for " + city + " already exists. To regather this data, you must delete the following file: /CityData/" + city + "_data.csv")
    else:
        retrieveCityData(city, cityApiInfo[city]["url"])