import csv 
import datetime

philly = False
baltimore = False
omaha = True

fields1 = ["id", "date", "time", "offense", "latitude", "longitude"]
fields = ["id", "date", "offense", "latitude", "longitude"]
dataList = []
num = 0

if philly:
  with open("./UnparsedCityCSVs/Philadelphia/incidents_2019.csv", 'r') as file:
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


  with open("./UnparsedCityCSVs/Philadelphia/incidents_2020.csv", 'r') as file:
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


  with open("./UnparsedCityCSVs/Philadelphia/incidents_2021.csv", 'r') as file:
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



  filename = "./CityData/Philadelphia_Data.csv"

  with open(filename, 'w') as csvfile: 
      # creating a csv writer object 
      csvwriter = csv.writer(csvfile) 
          
      # writing the fields1 
      csvwriter.writerow(fields1) 
          
      # writing the data rows 
      csvwriter.writerows(dataList)

if baltimore:
  with open("./UnparsedCityCSVs/Baltimore/CrimeData_2012_to_2022.csv", 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      if num == 0:
          num = num + 1
          continue
      date = row[3].split(" ")[0]
      if(datetime.datetime(int(date.split("/")[0]), int(date.split("/")[1]), int(date.split("/")[2])) >= datetime.datetime(2019, 1, 1) 
        and datetime.datetime(int(date.split("/")[0]), int(date.split("/")[1]), int(date.split("/")[2]))<= datetime.datetime(2021, 12, 31)):

        datalist2 = []
        id = num
        time = row[3].split(" ")[1]
        offense = row[6]
        latitude = row[16]
        longitude = row[17]
        datalist2 = [id, date, time, offense, latitude, longitude]
        dataList.append(datalist2)
        num = num + 1
        print(num)
      # if num == 10:
      #   break
  # print(dataList)
  
  filename = "./CityData/Baltimore_Data.csv"

  with open(filename, 'w') as csvfile: 
      # creating a csv writer object 
      csvwriter = csv.writer(csvfile) 
          
      # writing the fields1 
      csvwriter.writerow(fields1) 
          
      # writing the data rows 
      csvwriter.writerows(dataList)


if omaha:
  with open("./UnparsedCityCSVs/Omaha/Incidents_2019.csv", 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      if num == 0:
        num = num + 1
        continue
      
      datalist2 = []
      id = num
      date = row[1]
      offense = row[3]
      latitude = row[6]
      longitude = row[7]
      datalist2 = [id, date, offense, latitude, longitude]
      dataList.append(datalist2)
      num = num + 1
      print(num)



  with open("./UnparsedCityCSVs/Omaha/Incidents_2020.csv", 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      datalist2 = []
      id = num
      date = row[1]
      offense = row[3]
      latitude = row[6]
      longitude = row[7]
      datalist2 = [id, date, offense, latitude, longitude]
      dataList.append(datalist2)
      num = num + 1
      print(num)


  with open(".//UnparsedCityCSVs/Omaha/Incidents_2021.csv", 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
      datalist2 = []
      id = num
      date = row[1]
      offense = row[3]
      latitude = row[6]
      longitude = row[7]
      datalist2 = [id, date, offense, latitude, longitude]
      dataList.append(datalist2)
      num = num + 1
      print(num)



  filename = "./CityData/Omaha_data.csv"

  with open(filename, 'w') as csvfile: 
      # creating a csv writer object 
      csvwriter = csv.writer(csvfile) 
          
      # writing the fields
      csvwriter.writerow(fields) 
          
      # writing the data rows 
      csvwriter.writerows(dataList)



