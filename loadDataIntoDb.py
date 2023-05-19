import pymysql
import pandas as pd
from pathlib import Path
import numpy as np
from sqlalchemy import create_engine, delete

def findLastDate(city, engine):
    with engine.connect() as conn:
        result = conn.execute('SELECT Date FROM SeniorDesign.CrimeData WHERE City="'+city+'" ORDER BY Date desc LIMIT 1;').first()
        return result
    
def checkCityCrimTotals(city, year, engine):
    with engine.connect() as conn:
        result = conn.execute('SELECT city FROM SeniorDesign.CrimeTypeTotals WHERE City="'+city+'" AND year="'+year+'" LIMIT 1;').first()
        return result

def copy_query(c, data, table_name, city):
    print('Importing Data for '+city)
    data.to_sql(table_name, con = c, if_exists = 'append', chunksize = 1000, index=False)

if __name__ == "__main__":
    directory = './StandardizedCityData/'
    files = Path(directory).glob('*')
    try:
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"  
                      .format(user="admin", pw="password!", host='seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com',
                      db="SeniorDesign"))
        
        print("Connected to MySql DB")

        table_n = "CrimeData"

        
        citiesLeft = ["Auburn", "Gainesville", "Oakland"]
        for file in files:
            data = pd.read_csv(file)
            city = file.name.split('_')[0]
            if(city not in citiesLeft):
                continue
            cityNameDf = [city] * len(data)
            data["city"] = cityNameDf
            data["date"] = pd.to_datetime(data["date"]).dt.date
            data = data[list(
                ('city', 'state', 'offense', 'crime_type', 'date', 'latitude', 'longitude'))]

            # print("Deleting data for " + city)
            # with engine.connect() as conn:
            #     conn.execute("DELETE FROM CrimeData WHERE city='"+city+"'")
            

            # Un comment this out to load new records into CrimeData
            lastDate = findLastDate(city, engine)
            newData = data
            if(lastDate != None):
                newData = data.loc[(data['date'] > findLastDate(city, engine)[0])]
            
            if(not newData.empty):
                copy_query(engine, newData, table_n, city)
            else:
                print("No new data for "+city)


            crimeTotalData = pd.DataFrame(columns=["city", 'homicide', 'agg_assault', 'rape', 
                                                  'robbery', 'violent', 'theft', 'burglary', 'arson', 'vehicle_theft', 'property', 
                                                  'total', 'year'])
            
            data['Year'] = pd.to_datetime(data['date'], errors='coerce').dt.strftime('%Y')
            tempCrimeCount = data.groupby(["offense", "Year"]).size()
            tempCrimeTypeCount = data.groupby(["crime_type", "Year"]).size()

            for year in data["Year"].unique():
                print("Calculating " + city + " crime totals for " + year)
                cityCrimeTotals = checkCityCrimTotals(city, year, engine)
                if(not cityCrimeTotals):
                    if("Homicide" in tempCrimeCount and year in tempCrimeCount["Homicide"]):
                        homicideCount = tempCrimeCount["Homicide"][year]
                    else:
                        homicideCount = 0
                    
                    if("Aggrevated Assault" in tempCrimeCount and year in tempCrimeCount["Aggrevated Assault"]):
                        aggCount = tempCrimeCount["Aggrevated Assault"][year]
                    else:
                        aggCount = 0

                    if("Rape" in tempCrimeCount and year in tempCrimeCount["Rape"]):
                        rapeCount = tempCrimeCount["Rape"][year]
                    else:
                        rapeCount = 0

                    if("Robbery" in tempCrimeCount and year in tempCrimeCount["Robbery"]):
                        robberyCount = tempCrimeCount["Robbery"][year]
                    else:
                        robberyCount = 0

                    if("Motor Vehicle Theft" in tempCrimeCount and year in tempCrimeCount["Motor Vehicle Theft"]):
                        vehicleCount = tempCrimeCount["Motor Vehicle Theft"][year]
                    else:
                        vehicleCount = 0

                    if("Larceny-Theft" in tempCrimeCount and year in tempCrimeCount["Larceny-Theft"]):
                        theftCount = tempCrimeCount["Larceny-Theft"][year]
                    else:
                        theftCount = 0

                    if("Burglary" in tempCrimeCount and year in tempCrimeCount["Burglary"]):
                        burglaryCount = tempCrimeCount["Burglary"][year]
                    else:
                        burglaryCount = 0

                    if("Arson" in tempCrimeCount and year in tempCrimeCount["Arson"]):
                        arsonCount = tempCrimeCount["Arson"][year]
                    else:
                        arsonCount = 0

                    violentCount = tempCrimeTypeCount["VIOLENT"][year]
                    properyCount = tempCrimeTypeCount["PROPERTY"][year]

                    if("OTHER" in tempCrimeTypeCount):
                        otherCount = tempCrimeTypeCount["OTHER"][year]
                    else:
                        otherCount = 0

                    total = (data["Year"] == year).sum()

                    tempCrimeTotalData = {"city": [city], 'homicide': [homicideCount], 'agg_assault': [aggCount], 'rape': [rapeCount], 
                                                    'robbery': [robberyCount], 'violent': [violentCount], 
                                                    'theft': [theftCount], 'burglary': [burglaryCount], 'arson': [arsonCount], 
                                                    'vehicle_theft': [vehicleCount], 'property': [properyCount], 'other': [otherCount], 
                                                    'total': [total], 'year': [year]}
                    
                    crimeTotalData = pd.DataFrame(data=tempCrimeTotalData)
                    crimeTotalData = crimeTotalData[list(
                    ("city", 'homicide', 'agg_assault', 'rape', 
                                                    'robbery', 'violent', 'theft', 'burglary', 'arson', 'vehicle_theft', 'property', 'other', 
                                                    'total', 'year'))]
                    copy_query(engine, crimeTotalData, "CrimeTypeTotals", city)
                else:
                    print("Crime total data already exists for "+city)

            

    except (Exception, pymysql.Error) as error:
        print("Error while connecting to MySql", error)
    finally:
        print("All city data has been imported to the database")
