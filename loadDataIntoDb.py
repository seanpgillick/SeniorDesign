import pymysql
import pandas as pd
from pathlib import Path
import numpy as np
from sqlalchemy import create_engine, delete

def findLastDate(city, engine):
    with engine.connect() as conn:
        result = conn.execute('SELECT Date FROM SeniorDesign.CrimeData WHERE City="'+city+'" ORDER BY Date desc LIMIT 1;').first()
        return result

def copy_query(c, data, table_name, city):
    print('Importing Data for '+city)
    data.to_sql('CrimeData', con = c, if_exists = 'append', chunksize = 1000, index=False)

if __name__ == "__main__":
    directory = './StandardizedCityData/'
    files = Path(directory).glob('*')
    try:
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"  
                      .format(user="admin", pw="password!", host='seniordesign-db.cxwhjsfccgui.us-east-1.rds.amazonaws.com',
                      db="SeniorDesign"))
        
        print("Connected to MySql DB")

        table_n = "CrimeData"

        # with engine.connect() as conn:
        #     conn.execute("DELETE FROM CrimeData")

        for file in files:
            data = pd.read_csv(file)
            city = file.name.split('_')[0]
            cityNameDf = [city] * len(data)
            data["city"] = cityNameDf
            data["date"] = pd.to_datetime(data["date"]).dt.date
            data = data[list(
                ('city', 'date', 'offense', 'latitude', 'longitude'))]

            lastDate = findLastDate(city, engine)

            if(lastDate != None):
                data = data.loc[(data['date'] > findLastDate(city, engine)[0])]
            
            if(not data.empty):
                copy_query(engine, data, table_n, city)
            else:
                print("No new data for "+city)
    except (Exception, pymysql.Error) as error:
        print("Error while connecting to MySql", error)
    finally:
        print("All city data has been imported to the database")
