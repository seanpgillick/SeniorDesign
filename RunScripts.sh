#!/bin/bash

#This will run all of the scripts in order

#Call APIs
python retrieveSocrataApiData.py
python retrieveCSVData.py

######Takes very long to run. Should be run by themselves before data is entered into the database.
######python convertAddresstoLatLong.py HOUSTON
######python convertAddresstoLatLong.py MILWALKEE

#Reformat Data
python reformatCSData.py
python reformatKCData.py

#Standardizing
python standardizeDates.py
python standardizeCrimeTypes.py
python addStateAbbreviationsColumn.py

#Populate Database with CSV Data
python loadDataIntoDb.py
python createCityInformationTables.py
