import pymysql
import pandas as pd
from pathlib import Path
import numpy as np
from sqlalchemy import create_engine, delete
import requests

#This Data is coming from Wikipedia
cityAreas= {
    "Atlanta": 136.3,
    "Austin": 271.8,
    "Auburn": 29.87,
    "Baltimore": 92.28,
    "Baton Rouge": 88.52,
    "Boston": 89.63,
    "Buffalo": 52.51,
    "Chicago": 234.5,
    "Cincinnati": 79.64,
    "Colorado Springs": 195.8,
    "Fort Worth": 355.6,
    "Gainesville": 35.37,
    "Houston": 665,
    "Kansas City": 319,
    "Los Angeles": 502,
    "Memphis": 302.6,
    "Mesa": 133.1,
    "Milwaukee": 96.82,
    "Minneapolis": 57.51,
    "Nashville": 526,
    "New York": 302.6,
    "Oakland": 78.03,
    "Omaha": 146.3,
    "Philadelphia": 141.7,
    "Portland": 145,
    "Raleigh": 149.6,
    "San Francisco": 46.87,
    "Seattle": 83.78,
}

stateabbreviations = {
    "Atlanta": "GA",
    "Austin": "TX",
    "Auburn": "AL",
    "Baltimore": "MD",
    "Baton Rouge": "LA",
    "Boston": "MA",
    "Buffalo": "NY",
    "Chicago": "IL",
    "Cincinnati": "OH",
    "Colorado Springs": "CO",
    "Fort Worth": "TX",
    "Gainesville": "FL",
    "Houston": "TX",
    "Kansas City": "MO",
    "Los Angeles": "CA",
    "Memphis": "TN",
    "Mesa": "AZ",
    "Milwaukee": "WI",
    "Minneapolis": "MN",
    "Nashville": "TN",
    "New York": "NY",
    "Oakland": "CA",
    "Omaha": "NE",
    "Philadelphia": "PA",
    "Portland": "OR",
    "Raleigh": "NC",
    "San Francisco": "CA",
    "Seattle": "WA",
}

# Data gathered from Google
cityPopulations2019 = {
    "Atlanta": {
        "2019": 507301
    },
    "Austin": {
        "2019": 978763
    },
    "Auburn": {
        "2019": 81399,
        "2020": 87143,
        "2021": 85699
    },
    "Baltimore": {
        "2019": 594601
    },
    "Baton Rouge": {
        "2019": 220787
    },
    "Boston": {
        "2019": 694661
    },
    "Buffalo": {
        "2019": 255317
    },
    "Chicago": {
        "2019": 2691000
    },
    "Cincinnati": {
        "2019": 304445
    },
    "Colorado Springs": {
        "2019": 478035
    },
    "Fort Worth": {
        "2019": 908491
    },
    "Gainesville":{
        "2019": 134188
    },
    "Houston": {
        "2019": 2316000
    },
    "Kansas City": {
        "2019": 496299
    },
    "Los Angeles": {
        "2019": 3983000
    },
    "Memphis": {
        "2019": 650998
    },
    "Mesa": {
        "2019": 518497
    },
    "Milwaukee": {
        "2019": 590952
    },
    "Minneapolis": {
        "2019": 428821
    },
    "Nashville": {
        "2019": 1224000
    },
    "New York": {
        "2019": 8343000
    },
    "Oakland": {
        "2019": 422738
    },
    "Omaha": {
        "2019": 477766
    },
    "Philadelphia": {
        "2019": 1584000
    },
    "Portland": {
        "2019": 654378
    },
    "Raleigh": {
        "2019": 474255
    },
    "San Francisco": {
        "2019": 878826
    },
    "Seattle": {
        "2019": 753291
    },
}

csvYearPopulations = ["2020", "2021"]

def checkCityInfo(city):
    with engine.connect() as conn:
        result = conn.execute('SELECT city FROM SeniorDesign.CityInformation WHERE City="'+city+'" LIMIT 1;').first()
        return result
    
def checkCityPopulation(city, year, engine):
    with engine.connect() as conn:
        result = conn.execute('SELECT city FROM SeniorDesign.CityPopulations WHERE City="'+city+'" AND Year="'+year+'" LIMIT 1;').first()
        return result

def copy_query(c, data, table_name, city):
    print('Importing Data for '+city)
    data.to_sql(table_name, con = c, if_exists = 'append', chunksize = 1000, index=False)

if __name__ == "__main__":
    try:
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"  
                      .format(user="admin", pw="password!", host='seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com',
                      db="SeniorDesign"))
        
        print("Connected to MySql DB")

        populationData = pd.read_csv('./cityPopulations.csv')

        for city in cityAreas:

            # Get city populations for 2020 and 2021 from csv
            for year in csvYearPopulations:
                if(checkCityPopulation(city, year, engine)):
                    continue
                cityStateString = city+" ("+stateabbreviations[city]+")"
                if(city == "Nashville"):
                    cityStateString = "Nashville-Davidson (TN)"
                elif (city == "Washington D.C."):
                    cityStateString = "WASHINGTON (DC)"
                elif (city == "Auburn"):
                    continue
                cityPopulationData = populationData[populationData.City == cityStateString]
                cityYearPopulationData = cityPopulationData[cityPopulationData.Year == year]
                population = cityYearPopulationData.iloc[0]["Value"]
                tempCityPopulation = {"city": [city], 'state': [stateabbreviations[city]], 'population': [population], 'year': [year]}
                    
                cityPopulation = pd.DataFrame(data=tempCityPopulation)
                cityPopulation = cityPopulation[list(
                ("city", 'state', 'population', 'year'))]
                copy_query(engine, cityPopulation, "CityPopulations", city)

            # Insert populations from population 2019 dictionary
            if(not checkCityPopulation(city, "2019", engine)):
                population2019 = cityPopulations2019[city]["2019"]
                tempCityPopulation = {"city": [city], 'state': [stateabbreviations[city]], 'population': [population2019], 'year': ["2019"]}
                cityPopulation = pd.DataFrame(data=tempCityPopulation)
                cityPopulation = cityPopulation[list(
                ("city", 'state', 'population', 'year'))]
                copy_query(engine, cityPopulation, "CityPopulations", city)
            
            # Insert 2020 and 2021 from population dictionary for Auburn since it is not in the population csv
            if(city == "Auburn"):
                if(not checkCityPopulation(city, "2020", engine)):
                    population2020 = cityPopulations2019[city]["2020"]
                    tempCityPopulation = {"city": [city], 'state': [stateabbreviations[city]], 'population': [population2019], 'year': ["2020"]}
                    cityPopulation = pd.DataFrame(data=tempCityPopulation)
                    cityPopulation = cityPopulation[list(
                    ("city", 'state', 'population', 'year'))]
                    copy_query(engine, cityPopulation, "CityPopulations", city)

                if(not checkCityPopulation(city, "2021", engine)):
                    population2020 = cityPopulations2019[city]["2021"]
                    tempCityPopulation = {"city": [city], 'state': [stateabbreviations[city]], 'population': [population2019], 'year': ["2021"]}
                    cityPopulation = pd.DataFrame(data=tempCityPopulation)
                    cityPopulation = cityPopulation[list(
                    ("city", 'state', 'population', 'year'))]
                    copy_query(engine, cityPopulation, "CityPopulations", city)

            # Check if city information already in db
            if(checkCityInfo(city)):
                print("City Information Already exists for "+city)
                continue
            
            
            # Use ninja city api to get latitude and longitude
            if(city == "Washington D.C."):
                api_url = 'https://api.api-ninjas.com/v1/city?name={}'.format("Washington")
            else:
                api_url = 'https://api.api-ninjas.com/v1/city?name={}'.format(city)

            response = requests.get(api_url, headers={'X-Api-Key': '8tfSJTfZDFjVpnvHPJzbiw==rpOFNVcoiNahUyK3'})
            
            if response.status_code == requests.codes.ok:
                latitude = response.json()[0]["latitude"]
                longitude = response.json()[0]["longitude"]

                tempCityInfo = {"city": [city], 'state': [stateabbreviations[city]], 'area': [cityAreas[city]], 'latitude': [latitude], 'longitude': [longitude]}
                    
                cityInfo = pd.DataFrame(data=tempCityInfo)
                cityInfo = cityInfo[list(
                ("city", 'state', 'area', 'latitude', 'longitude'))]

                copy_query(engine, cityInfo, "CityInformation", city)
            else:
                print("Error:", response.status_code, response.text)
        
    except (Exception, pymysql.Error) as error:
        print("Error while connecting to MySql", error)
    finally:
        print("All city data has been imported to the database")