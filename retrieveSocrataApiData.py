# Main goal of this script is to retrieve data from the Socrata API and save it to a csv file in the CityData folder
# cityApiInfo is a dictionary that contains the information of each city that needed to be retrieved

from operator import truediv
from select import select
import sys
import pandas as pd
from sodapy import Socrata
import datetime
from pathlib import Path
import retrieveCSVData

# This dictionary stores socrata API information
# If your city uses socrata you can add it's information to this dictionary
# dateCol --> The cities date column title
# offCol --> The cities offense column title
# latCol --> The cities latitude column title
# lonCol --> The cities longitue column title

cityApiInfo = {
    "New York": {
        "url": "data.cityofnewyork.us",
        "dateCol": "cmplnt_fr_dt",
        "offCol": "ofns_desc",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["qgea-i56i"]
    },
    "Los Angeles": {
        "url": "data.lacity.org",
        "dateCol": "date_occ",
        "offCol": "crm_cd_desc",
        "latCol": "lat",
        "lonCol": "lon",
        "keys": ["63jg-8b9z", "2nrs-mtv8"]
    },
    "Chicago": {
        "url": "data.cityofchicago.org",
        "dateCol": "date",
        "offCol": "primary_type",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["ijzp-q8t2"]
    },
    "Cincinnati": {
        "url": "data.cincinnati-oh.gov",
        "dateCol": "date_reported",
        "offCol": "offense",
        "latCol": "latitude_x",
        "lonCol": "longitude_x",
        "keys": ["k59e-2pvf"]
    },
    "Austin": {
        "url": "data.austintexas.gov",
        "dateCol": "occ_date_time",
        "offCol": "category_description",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["fdj4-gpfu"]
    },
    "Atlanta": {
        "url": "sharefulton.fultoncountyga.gov",
        "dateCol": "reportdate",
        "offCol": "ucrliteral",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["9w3w-ynjw"]
    },
    "Memphis": {
        "url": "data.memphistn.gov",
        "dateCol": "offense_date",
        "offCol": "agency_crimetype_id",
        "latCol": "coord1",
        "lonCol": "coord2",
        "keys": ["ybsi-jur4"]
    },
    "San Francisco": {
        "url": "data.sfgov.org",
        "dateCol": "incident_date",
        "offCol": "incident_category",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["wg3w-h783"]
    },
    "Seattle": {
        "url": "data.seattle.gov",
        "dateCol": "offense_start_datetime",
        "offCol": "offense",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["tazs-3rd5"]
    },
    "Colorado Springs": {  # LOCATION IS ALL IN ONE PIECE, WILL NEED TO SPLIT
        "url": "policedata.coloradosprings.gov",
        "dateCol": "reporteddate",
        "offCol": "CrimeCodeDescription",
        "latCol": "location_point",
        "lonCol": "location_point",
        "keys": ["bc88-hemr"]
    },
    "Mesa": {
        "url": "data.mesaaz.gov",
        "dateCol": "occurred_date",
        "offCol": "crime_type",
        "latCol": "latitude",
        "lonCol": "longitude",
        "keys": ["39rt-2rfj"]
    },
    "Kansas City": {  # LOCATION IS ALL IN ONE PIECE, WILL NEED TO SPLIT
        "url": "data.kcmo.org",
        "dateCol": "reported_date",
        "offCol": "offense",
        "latCol": "location",
        "lonCol": "location",
        "keys": ["pxaa-ahcm", "vsgj-uufz", "w795-ffu6"]
    },
    "Fort Worth": {
            "url":"data.fortworthtexas.gov",
            "dateCol":"from_date",
            "offCol":"nature_of_call",
            "latCol":"location_1",
            "lonCol":"location_type",
            "keys":["k6ic-7kp7"]
        },
    "Nashville": {
            "url":"data.nashville.gov",
            "dateCol":"incident_reported",
            "offCol":"offense_nibrs",
            "latCol":"latitude",
            "lonCol":"longitude",
            "keys":["2u6v-ujjs"]
        },
    "Buffalo": {
            "url":"data.buffalony.gov",
            "dateCol":"incident_datetime",
            "offCol":"incident_type_primary",
            "latCol":"latitude",
            "lonCol":"longitude",
            "keys":["d6g9-xbgu"]
        },
    "Montgomery": {
            "url":"data.montgomerycountymd.gov",
            "dateCol":"date",
            "offCol":"nibrs_code",
            "latCol":"latitude",
            "lonCol":"longitude",
            "keys":["icn6-v9z3"]
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
    selectString = dateCol+" as date,"+offCol+" as offense," + \
        latCol+" as latitude,"+lonCol+" as longitude"
    whereString = dateCol + " >= '2019-01-01' and " + dateCol + " < '2022-01-01'"

    # Loop through the cities different endpoints
    for key in keys:
        # Change dateCol string if gathering data for Kansas City 2021
        if city == "Kansas City" and key == "w795-ffu6":
            dateCol = "report_date"
            selectString = dateCol+" as date,"+offCol+" as offense," + \
                latCol+" as latitude,"+lonCol+" as longitude"
            whereString = dateCol + " >= '2019-01-01' and " + dateCol + " < '2022-01-01'"

        looping = True
        offset = 0

        # Retrieve city data 2000 rows at a time
        while looping:
            results = client.get(key, limit=2000, offset=offset,
                                 where=whereString, select=selectString, order=dateCol)

            if (city == "Fort Worth"):
                for row in results:
                    try:
                        row['longitude'] = row['latitude']['longitude']
                        row['latitude'] = row['latitude']['latitude']
                    except Exception as e:
                        print("Could not get latitude, longitude: " + str(e))
                        row['longitude'] = "Not Available"
                        row['latitude'] = "Not Available"
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

    if (path.is_file()):
        print("Csv for " + city + " already exists. To regather this data, you must delete the following file: /CityData/" + city + "_data.csv")
    else:
        retrieveCityData(city, cityApiInfo[city]["url"], cityApiInfo[city]["dateCol"], cityApiInfo[city]["offCol"], cityApiInfo[city]["latCol"],
                         cityApiInfo[city]["lonCol"], cityApiInfo[city]["keys"])

retrieveCSVData.collectCSVData()
# url for proper DC query https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer/2/query?where=1%3D1&outFields=OFFENSE,LATITUDE,LONGITUDE,START_DATE,END_DATE,REPORT_DAT&outSR=4326&f=json
