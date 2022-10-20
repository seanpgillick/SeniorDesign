import csv 

fields = ["id", "date", "time", "offense", "latitude", "longitude"]
dataList = []
num = 0

with open("./CityData/incidents_2019.csv", 'r') as file:
  csvreader = csv.reader(file)
  for row in csvreader:
    if num == 0:
      num = num + 1
      continue
    
    datalist2 = []
    id = num
    date = row[4]
    time = row[5]
    offense = row[10]
    latitude = row[13]
    longitude = row[14]
    datalist2 = [id, date, time, offense, latitude, longitude]
    dataList.append(datalist2)
    num = num + 1
    print(num)


with open("./CityData/incidents_2020.csv", 'r') as file:
  csvreader = csv.reader(file)
  for row in csvreader:
    datalist2 = []
    id = num
    date = row[7]
    time = row[8]
    offense = row[13]
    latitude = row[16]
    longitude = row[17]
    datalist2 = [id, date, time, offense, latitude, longitude]
    dataList.append(datalist2)
    num = num + 1
    print(num)


with open("./CityData/incidents_2021.csv", 'r') as file:
  csvreader = csv.reader(file)
  for row in csvreader:
    datalist2 = []
    id = num
    date = row[7]
    time = row[8]
    offense = row[13]
    latitude = row[16]
    longitude = row[17]
    datalist2 = [id, date, time, offense, latitude, longitude]
    dataList.append(datalist2)
    num = num + 1
    print(num)



filename = "Philadelphia_Data.csv"

with open(filename, 'w') as csvfile: 
    # creating a csv writer object 
    csvwriter = csv.writer(csvfile) 
        
    # writing the fields 
    csvwriter.writerow(fields) 
        
    # writing the data rows 
    csvwriter.writerows(dataList)

  
# Closing file
# f.close()