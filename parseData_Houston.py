from operator import truediv
from select import select
import sys
import pandas as pd
from pathlib import Path
from geopy.geocoders import Nominatim

# assign directory
directory = './UnparsedCityCSVs/Houston'

city = "houston"
locator = Nominatim(user_agent="myGeocoder")
houstonCSVInfo = ["2019", "2020", "2021"]

final_df = pd.DataFrame()

seenAddressess = dict()
# get csv data
for year in houstonCSVInfo:
    filename = city + "_data_" + year + ".csv"
    print("Opening " + filename)
    path = Path("./UnparsedCityCSVs/Houston/"+filename)
    if (not path.is_file()):
        print("Unable to open file: " + filename)
    else:
        # Open the csv file
        colnames = ["a", "date", "b", "g", "offense", "c", "d", "e", "street number",
                    "street name", "street type", "suffix", "f", "zipCode"]
        data = pd.read_csv(path, names=colnames, skiprows=(0,),
                           usecols=["date", "offense", "street number", "street name", "street type", "suffix", "zipCode"])

        # get lat long for each incident
        latitudes = ["Not Available"] * data.shape[0]
        longitudes = ["Not Available"] * data.shape[0]

        print("Gettings latitude and longitudes")
        for ind in data.index:
            # check if suffix is null
            suffix = str(data["suffix"][ind])
            if (pd.isna(data["suffix"][ind])):
                suffix = ""

            # check if street number is null
            streetNum = str(data["street number"][ind])
            if (pd.isna(data["street number"][ind])):
                streetNum = ""

            # check if streeet type is null
            streetType = str(data["street type"][ind])
            if (pd.isna(data["street type"][ind])):
                streetType = ""

            address = streetNum + " " + str(data["street name"][ind]) + " " + \
                streetType + " " + suffix + " " + str(data["zipCode"][ind])
            print(data.shape[0]-ind)
            if address in seenAddressess:
                data["latitude"] = seenAddressess[address]["lat"]
                data["longitude"] = seenAddressess[address]["lon"]
            else:
                try:
                    location = locator.geocode(address)
                    if (location != None):
                        latitudes[ind] = location.latitude
                        longitudes[ind] = location.longitude
                        seenAddressess[address] = {
                            "lat": location.latitude, "lon": location.longitude}
                    else:
                        seenAddressess[address] = {
                            "lat": latitudes[ind], "lon": longitudes[ind]}
                except:
                    seenAddressess[address] = {
                        "lat": latitudes[ind], "lon": longitudes[ind]}
                    continue
        data["latitude"] = latitudes
        data["longitude"] = longitudes
        final_df = pd.concat([final_df, data])

final_df.to_csv('./CityData/Houston_data.csv')
