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
    "Fort Worth": {
            "url":"data.fortworthtexas.gov",
            "dateCol":"from_date",
            "offCol":"nature_of_call",
            "latCol":"location_1",
            "lonCol":"location_type",
            "keys":["k6ic-7kp7"]
        }
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
            results = client.get(key, limit=2000, offset=offset, select=selectString, where=whereString, order=dateCol)
            
            for row in results:
                try:
                    row['longitude']=row['latitude']['longitude']
                    row['latitude']=row['latitude']['latitude']
                except Exception as e:
                    print("Could not get latitude, longitude: " + str(e))
                    row['longitude']="Not Available"
                    row['latitude']="Not Available"
                
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

def getCSVData():
    # assign directory
    directory = './UnparsedCityCSVs/Portland'

    city = "portland"
    #locator = Nominatim(user_agent="myGeocoder")
    portlandCSVInfo = ["2019", "2020", "2021"]

    final_df = pd.DataFrame()

    seenAddressess = dict()
    # get csv data
    for year in portlandCSVInfo:
        filename = "CrimeData-" + year + ".csv"
        print("Opening " + filename)
        path = Path("./UnparsedCityCSVs/Portland/"+filename)
        if (not path.is_file()):
            print("Unable to open file: " + filename)
        else:
            # Open the csv file
            colnames = ["Address","CaseNumber","CrimeAgainst","Neighborhood","OccurDate","OccurTime","OffenseCategory","OffenseType","OpenDataLat","OpenDataLon","OpenDataX","OpenDataY","ReportDate","OffenseCount"
]
            data = pd.read_csv(path, names=colnames, skiprows=(0,),
                            usecols=["ReportDate", "OffenseCategory", "OpenDataLat", "OpenDataLon"])
            for num, row in data.iterrows():
                if(pd.isna(row['OpenDataLat'])):
                    data.at[num, 'OpenDataLat']="Not Available"
                if(pd.isna(row['OpenDataLon'])):
                    data.at[num, 'OpenDataLon']="Not Available"
            # for row in data:
            #     print(row['OpenDataLat'])
            data2 = data[['ReportDate', 'OffenseCategory', 'OpenDataLat', 'OpenDataLon']]
    final_df = pd.concat([final_df, data2])
    final_df.columns=["date", "offense", "latitude", "longitude"]
    final_df.to_csv('./CityData/Portland_data.csv')


def getCSVDataMil():
    # assign directory
    directory = './UnparsedCityCSVs/Milwaukee'

    city = "portland"
    #locator = Nominatim(user_agent="myGeocoder")
    milwaukeeCSVInfo = ["2005-2021"]

    final_df = pd.DataFrame()

    seenAddressess = dict()
    # get csv data
    for year in milwaukeeCSVInfo:
        filename = "CrimeData-" + year + ".csv"
        print("Opening " + filename)
        path = Path("./UnparsedCityCSVs/Milwaukee/"+filename)
        if (not path.is_file()):
            print("Unable to open file: " + filename)
        else:
            # Open the csv file
            colnames = ["ReportedDateTime","Location","ZIP","RoughX","RoughY","Arson","AssaultOffense","Burglary","CriminalDamage","Homicide","LockedVehicle","Robbery","SexOffense","Theft","VehicleTheft"]
            offenseColnames = ["Arson","AssaultOffense","Burglary","CriminalDamage","Homicide","LockedVehicle","Robbery","SexOffense","Theft","VehicleTheft"]



            data = pd.read_csv(path, names=colnames, skiprows=(0,),
                            usecols=["ReportedDateTime", "Location","ZIP","RoughX","RoughY","Arson","AssaultOffense","Burglary","CriminalDamage","Homicide","LockedVehicle","Robbery","SexOffense","Theft","VehicleTheft"])
            
            data["offense"] = "Not Available"
            for num, row in data.iterrows():
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
            data = data[data['ReportedDateTime'].str.contains("2019") | data['ReportedDateTime'].str.contains("2020") | data['ReportedDateTime'].str.contains("2021")]
            data2=data[['ReportedDateTime', 'offense', 'RoughX', 'RoughY']]
            # for row in data:
            #     print(row['OpenDataLat'])
    final_df = pd.concat([final_df, data2])
    final_df.columns=["date", "offense", "latitude", "longitude"]
    final_df.to_csv('./CityData/Milwaukee_data.csv')



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

#getCSVData()
getCSVDataMil()



