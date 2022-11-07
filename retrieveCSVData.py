from operator import truediv
from select import select
import sys
import pandas as pd
from sodapy import Socrata
import datetime
from pathlib import Path

#when gathering csv data make sure to store it in ./UnprasedCityCSVs
#create a folder of the city
#each csv file should be cityName-year.csv (if multiple years do cityName-year-year.csv)


# This dictionary CSV file information
# If your city uses CSV you can add it's information to this dictionary
# dateCol --> The cities date column title
# offCol --> The cities offense column title
# latCol --> The cities latitude column title
# lonCol --> The cities longitue column title
# key    --> Stores the years that the csv file stores (should be the same for the years on the csv file name)


# this 
cityCSVInfo = {
    "Milwaukee": {
            "url": "./UnparsedCityCSVs/Milwaukee",
            "dateCol":"ReportedDateTime",
            "offCol":"offense",
            "latCol":"RoughX",
            "lonCol":"RoughY",
            "keys":["2005-2021"]
    },
    "Portland": {
            "url": "./UnparsedCityCSVs/Portland",
            "dateCol":"ReportDate",
            "offCol":"OffenseCategory",
            "latCol":"OpenDataLat",
            "lonCol":"OpenDataLon",
            "keys":["2019", "2020", "2021"]
    },
    "Houston": {
            "url": "./UnparsedCityCSVs/Houston",
            "dateCol": "date",
            "offCol": "offense",
            "latCol": "latitude",
            "lonCol": "longitude",
            "keys": ["2019", "2020", "2021"]
    }
}



def retrieveCityCSVData(city, url, dateCol, offCol, latCol, lonCol, keys):
    csvName = city + "_data.csv"
    final_df = pd.DataFrame()
    # assign directory
    finalCol = [dateCol, offCol, latCol, lonCol]
    #locator = Nominatim(user_agent="myGeocoder")

    final_df = pd.DataFrame()
    colnames=[]
    offenseColnames=[]
    # get csv data
    for year in keys:
        filename = "CrimeData-" + year + ".csv"
        print("Opening " + filename)

        path = Path(url+"/"+filename)
        if (not path.is_file()):
            print("Unable to open file: " + filename)
        else:
            # Open the csv file
            if(city=="Milwaukee"):
                colnames = ["ReportedDateTime","Location","ZIP","RoughX","RoughY","Arson","AssaultOffense","Burglary","CriminalDamage","Homicide",
                    "LockedVehicle","Robbery","SexOffense","Theft","VehicleTheft"]
                offenseColnames = ["Arson","AssaultOffense","Burglary","CriminalDamage","Homicide","LockedVehicle","Robbery","SexOffense","Theft","VehicleTheft"]
            elif(city=="Portland"):
                colnames = ["Address","CaseNumber","CrimeAgainst","Neighborhood","OccurDate","OccurTime",
                    "OffenseCategory","OffenseType","OpenDataLat","OpenDataLon","OpenDataX","OpenDataY","ReportDate","OffenseCount"]
            elif(city=="Houston"):
                colnames = ["a", "date", "b", "g", "offense", "latitude", "longitude", "e", "street number",
                    "street name", "street type", "suffix", "f", "zipCode"]

            data = pd.read_csv(path, names=colnames, skiprows=(0,))
            
            for num, row in data.iterrows():
                if(city=="Milwaukee"):
                    newOffense=""
                    for x in offenseColnames:
                        if(row[x]==1):
                            newOffense=x
                            break
                    data.at[num, 'offense']=newOffense
                    if(pd.isna(row['RoughX'])):
                        data.at[num, 'RoughX']="Not Available"
                    if(pd.isna(row['RoughY'])):
                        data.at[num, 'RoughY']="Not Available"
                elif(city=="Portland"):
                    if(pd.isna(row['OpenDataLat'])):
                        data.at[num, 'OpenDataLat']="Not Available"
                    if(pd.isna(row['OpenDataLon'])):
                        data.at[num, 'OpenDataLon']="Not Available"
                elif(city=="Houston"):
                    # check if suffix is null
                    suffix = str(data.at[num,"suffix"])
                    if (pd.isna(data.at[num,"suffix"])):
                        suffix = ""

                    # check if street number is null
                    streetNum = str(data.at[num, "street number"])
                    if (pd.isna(data.at[num, "street number"])):
                        streetNum = ""

                    # check if streeet type is null
                    streetType = str(data.at[num, "street type"])
                    if (pd.isna(data.at[num, "street type"])):
                        streetType = ""

                    address = streetNum + " " + str(data.at[num, "street name"]) + " " + \
                        streetType + " " + suffix + " " + str(data.at[num, "zipCode"])
                    data.at[num, 'latitude']=address
                    data.at[num, 'longitude']=""

                    
            if(city=="Milwaukee"):
                data = data[data[dateCol].str.contains("2019") | data[dateCol].str.contains("2020") | data[dateCol].str.contains("2021")]
            # for row in data:
            #     print(row['OpenDataLat'])
            data2 = data[finalCol]
    final_df = pd.concat([final_df, data2])
    final_df.columns=["date", "offense", "latitude", "longitude"]
    final_df.to_csv('./CityData/'+city+'_data.csv')



def collectCSVData():

    for city in cityCSVInfo:
        csvName = city + "_data.csv"
        path = Path('./CityData/'+csvName)

        print("\nGathering Data for " + city)

        if(path.is_file()):
            print("Csv for " + city + " already exists. To regather this data, you must delete the following file: /CityData/" + city + "_data.csv")
        else:
            
            retrieveCityCSVData(city, cityCSVInfo[city]["url"], cityCSVInfo[city]["dateCol"], cityCSVInfo[city]["offCol"], cityCSVInfo[city]["latCol"], 
            cityCSVInfo[city]["lonCol"], cityCSVInfo[city]["keys"]) 


collectCSVData()
