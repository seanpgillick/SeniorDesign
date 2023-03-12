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
    "Baltimore": 92.28,
    "Boston": 89.63,
    "Buffalo": 52.51,
    "Chicago": 234.5,
    "Cincinnati": 79.64,
    "Colorado Springs": 195.8,
    "Fort Worth": 355.6,
    "Houston": 665,
    "Kansas City": 319,
    "Los Angeles": 502,
    "Memphis": 302.6,
    "Mesa": 133.1,
    "Milwaukee": 96.82,
    "Minneapolis": 57.51,
    "Montgomery": 162.3,
    "Nashville": 526,
    "New York": 302.6,
    "Omaha": 146.3,
    "Philadelphia": 141.7,
    "Portland": 145,
    "Raleigh": 149.6,
    "San Francisco": 46.87,
    "Seattle": 83.78,
    "Washington D.C.": 68.35
}

stateabbreviations = {
    "Atlanta": "GA",
    "Austin": "TX",
    "Baltimore": "MD",
    "Boston": "MA",
    "Buffalo": "NY",
    "Chicago": "IL",
    "Cincinnati": "OH",
    "Colorado Springs": "CO",
    "Fort Worth": "TX",
    "Houston": "TX",
    "Kansas City": "MO",
    "Los Angeles": "CA",
    "Memphis": "TN",
    "Mesa": "AZ",
    "Milwaukee": "WI",
    "Minneapolis": "MN",
    "Montgomery": "AL",
    "Nashville": "TN",
    "New York": "NY",
    "Omaha": "NE",
    "Philadelphia": "PA",
    "Portland": "OR",
    "Raleigh": "NC",
    "San Francisco": "CA",
    "Seattle": "WA",
    "Washington D.C.": "DC",
}

def checkCityInfo(city):
    with engine.connect() as conn:
        result = conn.execute('SELECT city FROM SeniorDesign.CityInformation WHERE City="'+city+'" LIMIT 1;').first()
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

        # with engine.connect() as conn:
        #     conn.execute("DROP TABLE IF EXISTS CityInformation")
        #     conn.execute('CREATE TABLE CityInformation(id INT NOT NULL AUTO_INCREMENT, city varchar(45), state varchar(45), area FLOAT, latitude FLOAT, longitude FLOAT, PRIMARY KEY ( id ))')

        for city in cityAreas:
            
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