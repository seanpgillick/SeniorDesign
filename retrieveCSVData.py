# Main goal of this script is to retrieve data from CSV files of each city from ./UnparsedCityCSVs and save it to a csv file in the CityData folder
# cityApiInfo is a dictionary that contains the information of each city that needed to be retrieved

from operator import truediv
from select import select
import sys
import pandas as pd
from sodapy import Socrata
import datetime
from pathlib import Path

# when gathering csv data make sure to store it in ./UnparsedCityCSVs
# create a folder of the city
# each csv file should be cityName-year.csv (if multiple years do cityName-year-year.csv)


# This dictionary CSV file information
# If your city uses CSV you can add it's information to this dictionary
# dateCol --> The cities date column title
# offCol --> The cities offense column title
# latCol --> The cities latitude column title
# lonCol --> The cities longitue column title
# key    --> Stores the years that the csv file stores (should be the same for the years on the csv file name)


# Dictionary that stores the information of each city
# If your city uses CSV you can add it's information to this dictionary
cityCSVInfo = {
    "Milwaukee": {
        "url": "./UnparsedCityCSVs/Milwaukee",
        "dateCol": "ReportedDateTime",
        "offCol": "offense",
        "latCol": "RoughX",
        "lonCol": "RoughY",
        "keys": ["2005-2021"]
    },
    "Portland": {
        "url": "./UnparsedCityCSVs/Portland",
        "dateCol": "ReportDate",
        "offCol": "OffenseType",
        "latCol": "OpenDataLat",
        "lonCol": "OpenDataLon",
        "keys": ["2019", "2020", "2021"]
    },
    "Houston": {
        "url": "./UnparsedCityCSVs/Houston",
        "dateCol": "date",
        "offCol": "offense",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["2019", "2020", "2021"]
    },
    "Boston": {
        "url": "./UnparsedCityCSVs/Boston",
        "dateCol": "OCCURRED_ON_DATE",
        "offCol": "OFFENSE_DESCRIPTION",
        "latCol": "Lat",
        "lonCol": "Long",
        "keys": ["2019", "2020", "2021"]
    },
    "Raleigh": {    ##### this city has data of 2018 
        "url": "./UnparsedCityCSVs/Raleigh",
        "dateCol": "reported_date",
        "offCol": "crime_description",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["2019-2021"]
    },
    "Minneapolis": {
        "url": "./UnparsedCityCSVs/Minneapolis",
        "dateCol": "reportedDate",
        "offCol": "description",
        "latCol": "centerLat",
        "lonCol": "centerLong",
        "keys": ["2019", "2020", "2021"]
    },
    "Omaha": {
        "url": "./UnparsedCityCSVs/Omaha",
        "dateCol": "date",
        "offCol": "offense",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["2019", "2020", "2021"]
    },
    "Philadelphia": {
        "url": "./UnparsedCityCSVs/Philadelphia",
        "dateCol": "date",
        "offCol": "offense",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["2019", "2020", "2021"]
    },
    "Baltimore": {
        "url": "./UnparsedCityCSVs/Baltimore",
        "dateCol": "CrimeDateTime",
        "offCol": "Description",
        "latCol": "Latitude",
        "lonCol": "Longitude",
        "keys": ["2012-2022"]
    },
}


def retrieveCityCSVData(city, url, dateCol, offCol, latCol, lonCol, keys):
    csvName = city + "_data.csv"
    final_df = pd.DataFrame()
    data2 = pd.DataFrame()
    # assign directory
    finalCol = [dateCol, offCol, latCol, lonCol]

    colnames = []
    offenseColnames = []
    # get csv data
    for year in keys:
        filename = "CrimeData-" + year + ".csv"
        print("Opening " + filename)

        path = Path(url+"/"+filename)
        if (not path.is_file()):
            print("Unable to open file: " + filename)
        else:
            # Open the csv file
            # For each city you must change the column names to match the column names of the csv file
            # The columns that are needed are dateCol, offCol, latCol, lonCol
            # We can use a,b,c,d... for the column names that we are not using (ex. if we are not using the YEAR column we can use "a" for the column name)
            if (city == "Milwaukee"):
                colnames = ["ReportedDateTime", "Location", "ZIP", "RoughX", "RoughY", "Arson", "AssaultOffense", "Burglary", "CriminalDamage", "Homicide",
                            "LockedVehicle", "Robbery", "SexOffense", "Theft", "VehicleTheft"]
                offenseColnames = ["Arson", "AssaultOffense", "Burglary", "CriminalDamage",
                                   "Homicide", "LockedVehicle", "Robbery", "SexOffense", "Theft", "VehicleTheft"]
            elif (city == "Portland"):
                colnames = ["Address", "CaseNumber", "CrimeAgainst", "Neighborhood", "OccurDate", "OccurTime",
                            "OffenseCategory", "OffenseType", "OpenDataLat", "OpenDataLon", "OpenDataX", "OpenDataY", "ReportDate", "OffenseCount"]
            elif (city == "Houston"):
                colnames = ["a", "date", "b", "g", "offense", "latitude", "longitude", "e", "street number",
                            "street name", "street type", "suffix", "f", "zipCode"]
            elif (city == "Boston"):
                colnames = ["INCIDENT_NUMBER", "OFFENSE_CODE", "OFFENSE_CODE_GROUP", "OFFENSE_DESCRIPTION", "DISTRICT", "REPORTING_AREA",
                            "SHOOTING", "OCCURRED_ON_DATE", "YEAR", "MONTH", "DAY_OF_WEEK", "HOUR", "UCR_PART", "STREET", "Lat", "Long", "Location"]
            elif (city == "Raleigh"):
                colnames = ["X", "Y", "OBJECTID", "GlobalID", "case_number", "crime_category", "crime_code", "crime_description", "crime_type", "reported_block_address", "city_of_incident",
                            "city", "district", "reported_date", "reported_year", "reported_month", "reported_day", "reported_hour", "reported_dayofwk", "latitude", "longitude", "agency", "updated_date"]
            elif (city == "Minneapolis"):
                colnames = ["X", "Y", "publicaddress", "caseNumber", "precinct", "reportedDate", "reportedTime", "beginDate", "reportedDateTime", "beginTime", "offense", "description",
                            "UCRCode", "enteredDate", "centergbsid", "centerLong", "centerLat", "centerX", "centerY", "neighborhood", "lastchanged", "LastUpdateDateETL", "OBJECTID"]
            elif (city == "Omaha"):
                colnames = ["a", "date", "c", "offense",
                            "e", "f", "latitude", "longitude"]
            elif (city == "Philadelphia"):
                # Condition for each year file since the column names are different
                if year == "2019":
                    colnames = [
                        "a", "b", "c", "d", "date", "f", "g", "h", "i", "j", "offense", "l", "m", "latitude", "longitude"]
                elif year == "2020" or year == "2021":
                    colnames = [
                        "a", "b", "c", "d", "x", "f", "g", "date", "h", "j", "z", "l", "m", "offense", "p", "o", "latitude", "longitude"]
            elif (city == "Baltimore"):
                colnames = ["a", "b", "c", "CrimeDateTime", "e", "f", "Description", "h", "i", "j", "k", "l", "m", "n", "o", "p", "Latitude", "Longitude", "s", "t", "u", "v", "w"]

            # Read the csv file
            data = pd.read_csv(path, names=colnames, skiprows=(0,), low_memory=False)

            for num, row in data.iterrows():
                # Specific condition for some cities to get its data retrived properly from the csv file
                if (city == "Milwaukee"):
                    newOffense = ""
                    for x in offenseColnames:
                        if (row[x] == 1):
                            newOffense = x
                            break
                    data.at[num, 'offense'] = newOffense
                    if (pd.isna(row['RoughX'])):
                        data.at[num, 'RoughX'] = "Not Available"
                    if (pd.isna(row['RoughY'])):
                        data.at[num, 'RoughY'] = "Not Available"
                elif (city == "Portland"):
                    if (pd.isna(row['OpenDataLat'])):
                        data.at[num, 'OpenDataLat'] = "Not Available"
                    if (pd.isna(row['OpenDataLon'])):
                        data.at[num, 'OpenDataLon'] = "Not Available"
                elif (city == "Houston"):
                    # check if suffix is null
                    suffix = str(data.at[num, "suffix"])
                    if (pd.isna(data.at[num, "suffix"])):
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
                        streetType + " " + suffix + " " + \
                        str(data.at[num, "zipCode"])
                    data.at[num, 'latitude'] = address
                    data.at[num, 'longitude'] = ""

                elif (city == "Boston"):
                    if (pd.isna(row['Lat'])):
                        data.at[num, 'Lat'] = "Not Available"
                    if (pd.isna(row['Long'])):
                        data.at[num, 'Long'] = "Not Available"
                elif (city == "Raleigh"):
                    if (pd.isna(row['latitude'])):
                        data.at[num, 'latitude'] = "Not Available"
                    if (pd.isna(row['longitude'])):
                        data.at[num, 'longitude'] = "Not Available"
                elif (city == "Minneapolis"):
                    if (pd.isna(row['centerLat'])):
                        data.at[num, 'centerLat'] = "Not Available"
                    if (pd.isna(row['centerLong'])):
                        data.at[num, 'centerLong'] = "Not Available"
            if (city == "Milwaukee"):
                data = data[data[dateCol].str.contains("2019") | data[dateCol].str.contains(
                    "2020") | data[dateCol].str.contains("2021")]
            elif (city == "Boston"):
                data = data[data[dateCol].str.contains("2019") | data[dateCol].str.contains(
                    "2020") | data[dateCol].str.contains("2021")]
            elif (city == "Minneapolis"):
                data = data[data[dateCol].str.contains("2019") | data[dateCol].str.contains(
                    "2020") | data[dateCol].str.contains("2021")]
            elif (city == "Baltimore"):
                data = data[data[dateCol].str.contains("2019") | data[dateCol].str.contains(
                    "2020") | data[dateCol].str.contains("2021")]

            data2 = pd.concat([data2, data[finalCol]])
    # Saving retrived data into a csv file in ./CityData
    final_df = pd.concat([final_df, data2])
    final_df.columns = ["date", "offense", "latitude", "longitude"]
    final_df.to_csv('./CityData/'+city+'_data.csv')


def collectCSVData():

    # Accessing each city from dictionary
    for city in cityCSVInfo:
        csvName = city + "_data.csv"
        path = Path('./CityData/'+csvName)

        print("\nGathering Data for " + city)

        # Check if the csv file already exists, if so skip it
        if (path.is_file()):
            print("Csv for " + city + " already exists. To regather this data, you must delete the following file: /CityData/" + city + "_data.csv")
        # Else call retrieveCityCSVData() to get the data
        else:
            retrieveCityCSVData(city, cityCSVInfo[city]["url"], cityCSVInfo[city]["dateCol"], cityCSVInfo[city]["offCol"], cityCSVInfo[city]["latCol"],
                                cityCSVInfo[city]["lonCol"], cityCSVInfo[city]["keys"])


collectCSVData()
