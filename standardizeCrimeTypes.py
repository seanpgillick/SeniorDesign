# Find similar crime types from each city

from operator import truediv
from select import select
import sys
import pandas as pd
from pathlib import Path
import threading
import os
import time
from tqdm import tqdm
import numpy as np

tqdm.pandas()

# This function takes in an offense and returns the standardized crime type
# Each if statement checks if the offense contains a certain keyword and returns the standardized crime type
def defineCrimeType(offense):
    offense = str(offense)
    # Check if Motor Vehicle Theft
    if (("theft" in offense.lower() and ("auto" in offense.lower() or "vehicle" in offense.lower()))
            or "mvt" in offense.lower() or "autoth" in offense.lower() or "mvthft" in offense.lower()):
        return "Motor vehicle Theft"
    # Check if Larceny-Theft
    if ("larceny" in offense.lower() and ("auto" not in offense.lower() or "vehicle" not in offense.lower())
            or "theft" in offense.lower() and ("auto" not in offense.lower() or "vehicle" not in offense.lower())):
        return "Larceny-Theft"
    # Check if Robbery
    if ("robbery" in offense.lower()):
        return "Robbery"
    # Check if Rape
    if ("rape" in offense.lower()):
        return "Rape"
    # Check if Burglary
    if ("burglary" in offense.lower() or "buglary" in offense.lower() or "burg" in offense.lower()):
        return "Burglary"
    # Check if Aggrevated Assault
    if ("assault" in offense.lower() and "ag" in offense.lower()):
        return "Aggrevated Assault"
    # Check if Assault
    if ("assault" in offense.lower() or "assualt" in offense.lower() or "assult" in offense.lower() or "assau" in offense.lower()):
        return "Assault"
    # Check if Arson
    if ("arson" in offense.lower()):
        return "Arson"
    # Check if murder
    if ("murder" in offense.lower() or "murdr" in offense.lower()):
        return "Murder"
    # Check if Sexual Assault
    if ("assault" in offense.lower() and "sexual" in offense.lower()):
        return "Sexual Assault"
    # Check if Homicide
    if ("homicide" in offense.lower()):
        return "Homicide"
    # Check if Kidnapping
    if ("kidnapping" in offense.lower()):
        return "Kidnapping"
    # Check if Fraud
    if ("fraud" in offense.lower()):
        return "Fraud"
    # Check if Shooting
    if ("shot" in offense.lower() or "shooting" in offense.lower()):
        return "Shooting"
    # Check if Vandalism
    if ("vandalism" in offense.lower()):
        return "Vandalism"
    # Check if Harassment
    if ("harassment" in offense.lower() or "harrasment" in offense.lower() or "harrassament" in offense.lower() or "harass" in offense.lower()):
        return "Harassment"

    return "Miscellaneous ("+offense+")"


def standardizeCrimeTypes(data, city):
    print("Standardizing Crime types for " + city)

    # Replace each offence of the data to the standardized crime type by calling defineCrimeType and passing the unstandardized offense
    data["offense"] = data['offense'].progress_apply(
        lambda x: defineCrimeType(x))
    data.to_csv('./StandardizedCityData/'+city+'_data.csv', index=False)


if __name__ == "__main__":
    directory = './CityData'
    files = Path(directory).glob('*')
    # Loop through all files in the directory to standardize crime types
    for file in files:
        data = pd.read_csv(file)
        
        #Passing data of the file and city name to the function
        standardizeCrimeTypes(data, file.name.split('_')[0])
