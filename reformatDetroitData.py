import csv
import json


f = open ('./UnparsedCityCSVs/Detroit/detroit_data_from_2017_to_2021.json', "r")
fields = ["id", "date", "time", "offense", "latitude", "longitude"]
dataList = []
  
# Reading from file
data = json.loads(f.read())
count = 1
  
# Iterating through the json
# list
for i in data['features']:
    item = 0
    boolVal = True
    for k in i['attributes']:
        id = count
        # print(k, ":", i['attributes'][k])
        
        if(item == 7):
            offense = i['attributes'][k]
        elif(item == 9):
            time = i['attributes'][k]
        elif(item == 12):
            year = i['attributes'][k]
            if(year < 2019 or year > 2021):
                boolVal = False
                break
        elif(item == 19):
            longitude = i['attributes'][k]
        elif(item == 20):
            latitude = i['attributes'][k]
        item+=1

    if(boolVal):
        dataList.append([id, year, time, offense, latitude, longitude])
        count += 1

filename = "./CityData/Detroit_data.csv"

with open(filename, 'w') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(fields) 
        
    # writing the data rows 
    csvwriter.writerows(dataList)
  
# Closing file
f.close()