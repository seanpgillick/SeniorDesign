#Main goal of this script is convert address to lat and long and update csv file inside CityData folder

from operator import truediv
from select import select
import sys
import pandas as pd
from pathlib import Path
import threading
from geopy.geocoders import Nominatim
import geocoder
import os
import time
from tqdm import tqdm

geolocator = Nominatim(user_agent="seniorProjectCityCrimeData")
tqdm.pandas()
# get csv data

#convert function to get lat and long for each address in dataframe and save it to csv file inside convertedAddresses folder
def convert(x, city):
    global failedCount
    try:
        location = geolocator.geocode(x, timeout=0.5)
        d = {"latitude": [location.latitude],
             "longitude": [location.longitude]}
        failedCount = 0
    except:
        d = {"latitude": ["Nan"], "longitude": ["Nan"]}
        failedCount += 1

    if (failedCount > 8):
        exit("Failed Count has exceeded 8. Api connection may have been lost")

    df = pd.DataFrame(data=d)
    df.to_csv('./convertedAddresses/'+city+'_latlng.csv',
              mode='a', index=False, header=False)


#With this function, we can convert the address to lat and long. Replacing CityData in CityData folder with lat and long info.
def getLatLong(dataframe, city):
    lastCheckedId = pd.read_csv(
        './convertedAddresses/'+city+'_latlng.csv').last_valid_index()
    if(lastCheckedId is None):
        lastCheckedId=1
    originalDataframe = dataframe
    dataframe = dataframe.iloc[lastCheckedId+1:]
    dataframe['Location'].progress_apply(lambda x: convert(x, city))  #calling convert function to get lat and long for each address in dataframe
    if (lastCheckedId == originalDataframe.shape[0]-1):
        latLngDataframe = pd.read_csv(
            './convertedAddresses/'+city+'_latlng.csv')
        originalDataframe[['latitude', 'longitude']] = latLngDataframe
        os.remove("./CityData/"+city+"_data.csv")
        originalDataframe.to_csv('./CityData/'+city+'_data.csv', index=False)


if __name__ == "__main__":
    failedCount = 0

    #Checking if path to CSV file is provided. If not exit.
    if (len(sys.argv) != 2):
        print("You have not supplied the correct number of arguments. This script should be used as follows: \n python ./convertAddressToLatLong.py 'path to city csv'")
        exit(0)

    #Checking if path to CSV file is valid. If not exit.
    path = Path(sys.argv[1])
    if (not path.is_file()):
        print("The file path '" + sys.argv[1] + "' does not exist")
        exit(0)

    #Getting city name and data to get Lat/Long
    city = path.name.split('_')[0]
    data = pd.read_csv(path)
    print(city)
    getLatLong(data, city)
