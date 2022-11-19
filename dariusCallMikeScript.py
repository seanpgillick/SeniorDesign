import convertAddressToLatLong
import csv


def callMain():
    finalOutput=""
    firstRun=True
    while(("Failed Count has exceeded" in finalOutput) or firstRun):
        firstRun=False
        f = open('Milwaukee_latlng.csv', "r+")
        lines = f.readlines()
        lines=lines[:-8]        
        f = open('Milwaukee_latlng.csv', "w+")
        f.writelines(lines)
        finalOutput = convertAddressToLatLong.mainCall("./CityData/Milwaukee_data.csv")
    return 0


callMain()