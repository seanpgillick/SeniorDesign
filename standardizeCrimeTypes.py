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

VIOLENT_CRIME = "VIOLENT"
PROPERTY_CRIME = "PROPERTY"
OTHER_CRIME = "OTHER"

# This function takes in an offense and returns the standardized crime type
# Each if statement checks if the offense contains a certain keyword and returns the standardized crime type
def defineCrimeType(offense):
    offense = str(offense)

    ## Check Violent Crime
    # Check if murder
    if ("murder" in offense.lower() or "murdr" in offense.lower() or "manslaughter" in offense.lower() 
        or "homicide" in offense.lower() or "09a" in offense.lower()):
        return "Homicide", VIOLENT_CRIME

    # Check if Aggrevated Assault
    if ("assault" in offense.lower() and "ag" in offense.lower() or "13a" in offense.lower() or ("battery" in offense.lower() and "agg" in offense.lower())):
        return "Aggrevated Assault", VIOLENT_CRIME

    # Check if Rape
    if ("rape" in offense.lower() or "sodomy" in offense.lower() 
        or ("sexual" in offense.lower() and ("assault" in offense.lower() or "battery" in offense.lower()))
        or "11" in offense.lower()):
        return "Rape", VIOLENT_CRIME

    # Check if Robbery
    if ("robbery" in offense.lower() or "carjacking" in offense.lower() or "120" in offense.lower()):
        return "Robbery", VIOLENT_CRIME

    ## Check Property Crime
    # Check if Motor Vehicle Theft
    if (("theft" in offense.lower() and ("auto" in offense.lower() or "vehicle" in offense.lower()))
            or "mvt" in offense.lower() or "autoth" in offense.lower() or "mvthft" in offense.lower() or "240" in offense.lower()):
        return "Motor Vehicle Theft", PROPERTY_CRIME

    # Check if Larceny-Theft
    if (("larceny" in offense.lower() or "theft" in offense.lower() or "stolen" in offense.lower()) 
        and ("auto" not in offense.lower() or "vehicle" not in offense.lower() or "mv" not in offense.lower() 
        or "attempt" not in offense.lower() or "veh" not in offense.lower() or "fail" not in offense.lower() or "identity" not in offense.lower())
        or ("shoplifting" in offense.lower() or ("pocket" in offense.lower() and "pick" in offense.lower()) or "purse-snatching" in offense.lower())
        or "larc" in offense.lower() or "23" in offense.lower()):
        return "Larceny-Theft", PROPERTY_CRIME

    # Check if Burglary
    if ("burglary" in offense.lower() or "buglary" in offense.lower() or "burg" in offense.lower() or "220" in offense.lower()):
        return "Burglary", PROPERTY_CRIME   

    # Check if Arson
    if ("arson" in offense.lower() or ("200" in offense.lower() and "$" not in offense.lower())):
        return "Arson", PROPERTY_CRIME


    # # Check if Assault
    # if ("assault" in offense.lower() or "assualt" in offense.lower() or "assult" in offense.lower() 
    #     or "assau" in offense.lower() or "aslt" in offense.lower() or "asslt" in offense.lower()):
    #     return "Assault", OTHER_CRIME

    # # Check if Sexual Assault
    # if (("sex" in offense.lower() and ("assault" in offense.lower() or "abuse" in offense.lower() or "offense" in offense.lower())) 
    #     or "fondling" in offense.lower()):
    #     return "Sexual Assault", OTHER_CRIME

    # # Check if Kidnapping
    # if ("kidnapping" in offense.lower()):
    #     return "Kidnapping", OTHER_CRIME

  
    # # Check if Shooting
    # if ("shot" in offense.lower() or "shooting" in offense.lower()):
    #     return "Shooting", OTHER_CRIME

    # # Check if Harassment
    # if (("harassment" in offense.lower() or "harrasment" in offense.lower() or "harrassament" in offense.lower() or "harass" in offense.lower())
    #     or ("threat" in offense.lower() and "phone" in offense.lower()) or ("obscene" in offense.lower() and "phone" in offense.lower())
    #     or ("violation" in offense.lower() and "protect" in offense.lower() and "order" in offense.lower())):
    #     return "Harassment", OTHER_CRIME

    # # Check if Child Abuse
    # if("offense" in offense.lower() and "children" in offense.lower()):
    #     return "Child Abuse", OTHER_CRIME

    # # Check if Human Trafficking
    # if ("human" in offense.lower() and "trafficking" in offense.lower()):
    #     return "Human Trafficking", OTHER_CRIME

    # #Check if Battery
    # if("battery" in offense.lower()):
    #     return "Battery", OTHER_CRIME

    # ## Check Crimes Against Property

    # # Check if Vandalism
    # if ("vandalism" in offense.lower() or ("criminal" in offense.lower() and "damage" in offense.lower())):
    #     return "Vandalism", OTHER_CRIME
    
    # ## Check Statutory Crimes
    # # Check if UUV
    # if ("uuv" in offense.lower()):
    #     return "UUV", OTHER_CRIME

    # # Check if Weapon Violation
    # if (("weapon" in offense.lower() or "concealed" in offense.lower()) 
    #     and ("violation" in offense.lower() or "offense" in offense.lower() or "offence" in offense.lower())):
    #     return "Weapon Violation", OTHER_CRIME
    
    # # Check if Drug Related Crime
    # if ("drug" in offense.lower() or "narcotic" in offense.lower() or "marijuana" in offense.lower()):
    #     return "Drug Related Crime", OTHER_CRIME
    
    # # Check if Alcohol Related Crim
    # if(("liquor" in offense.lower() and "violation" in offense.lower()) 
    #     or ("public" in offense.lower() and "drunk" in offense.lower()) or "drunkenness" in offense.lower()):
    #     return "Alcohol Related Crime", OTHER_CRIME

    # # Check if prostitution
    # if ("prostitution" in offense.lower()):
    #     return "Prostitution", OTHER_CRIME

    # # Check if Animal Cruelty
    # if(("animal" in offense.lower() and "cruelty" in offense.lower()) or "humane" in offense.lower()):
    #     return "Animal Cruelty", OTHER_CRIME

    # # Check for Obscenity 
    # if("pornography" in offense.lower() or "obscenity" in offense.lower() or ("obscene" in offense.lower() and "material" in offense.lower())):
    #     return "Obscenity", OTHER_CRIME

    # #Check Entry into Locked Vehicle
    # if("lockedvehicle" in offense.lower()):
    #     return "Entry into Locked Vehicle", OTHER_CRIME

    # # Check if disturbance of peace
    # if("peace" in offense.lower() and "violation" in offense.lower()):
    #     return "Disturbance of Peace", OTHER_CRIME

    # # Check Disorderly Conduct
    # if ("disorderly" in offense.lower() and "conduct" in offense.lower()):
    #     return "Disorderly Conduct", OTHER_CRIME

    # # Check indecent exposure
    # if("public" in offense.lower() and "indecency" in offense.lower()):
    #     return "Indecent Exposure", OTHER_CRIME

    # # Check if loitering
    # if("loitering" in offense.lower()):
    #     return "Loitering", OTHER_CRIME

    # # Check if Trespassing 
    # if("trespass" in offense.lower()):
    #     return "Trespassing", OTHER_CRIME

    # # Check if Stalking
    # if("stalking" in offense.lower()):
    #     return "Stalking", OTHER_CRIME

    # # Check if Illegal Gambling
    # if("gambling" in offense.lower() or "betting" in offense.lower()):
    #     return "Illegal Gambling", OTHER_CRIME

    # # Check if initidation
    # if("intimidation" in offense.lower()):
    #     return "Intimidation", OTHER_CRIME
    
    # # Check if Obstruction of Justice
    # if("interference" in offense.lower() and "officer" in offense.lower()):
    #     return "Obstruction of Justice", OTHER_CRIME

    # # Check if Petty Offense
    # if("other offense" in offense.lower()):
    #     return "Petty Offense", OTHER_CRIME
    
    # # Check non criminal
    # if("non-criminal" in offense.lower()):
    #     return "Non-Criminal Offense", OTHER_CRIME

    # # Check Ritualism
    # if("ritualism" in offense.lower()):
    #     return "Ritualism", OTHER_CRIME

    # # Check DUI
    # if("driving" in offense.lower() and "influence" in offense.lower()):
    #     return "DUI", OTHER_CRIME

    # # Check for Unauthorized Use of Motor Vehicle
    # if("unauthorized" in offense.lower() and "vehicle" in offense.lower()):
    #     return "Unauthorized Use of Motor Vehicle", OTHER_CRIME

    # # Check for traffic violation
    # if("traffic" in offense.lower() and "human" not in offense.lower()):
    #     return "Traffic Violation", OTHER_CRIME

    # # Check for Invasion of Privacy
    # if("peeping" in offense.lower()):
    #     return "Invasion of Privacy", OTHER_CRIME

    # # Check for Incest
    # if("incest" in offense.lower()):
    #     return "Incest", OTHER_CRIME

    # # Check for Status Offense
    # if("runaway" in offense.lower()):
    #     return "Status Offense", OTHER_CRIME

    # ## Check Financial Crimes
    # # Check if embezzlement
    # if ("embezzle" in offense.lower()):
    #     return "Embezzlement", OTHER_CRIME

    # # Check if extortion
    # if("extortion" in offense.lower()):
    #     return "Extortion", OTHER_CRIME

    # # Check if Forgery
    # if("forgery" in offense.lower()):
    #     return "Forgery", OTHER_CRIME

    # # Check if Fraud
    # if ("fraud" in offense.lower() or "swindle" in offense.lower()):
    #     return "Fraud", OTHER_CRIME

    # # Check Deceptive Practice
    # if (("deceptive" in offense.lower() and "practice" in offense.lower()) or "bad checks" in offense.lower()):
    #     return "Deceptive Practice", OTHER_CRIME

    # # Check Cybercrime
    # if("hacking" in offense.lower() or "computer" in offense.lower()):
    #     return "Cybercrime", OTHER_CRIME

    # # Check if Identity Theft
    # if("impersonation" in offense.lower() or ("identity" in offense.lower() and "theft" in offense.lower())):
    #     return "Identity Theft", OTHER_CRIME

    # ## Check Inchoate Crimes
    # # Check if Solicitation
    # if("bribery" in offense.lower()):
    #     return "Solicitation", OTHER_CRIME

    
    

    return "OTHER ("+offense+")", OTHER_CRIME


def standardizeCrimeTypes(data, city):
    print("Standardizing Crime types for " + city)

    data["reported_offense"] = data["offense"]

    # Replace each offence of the data to the standardized crime type by calling defineCrimeType and passing the unstandardized offense
    data["offense"], data["crime_type"] = zip(*data["offense"].progress_apply(
        lambda x: defineCrimeType(x)))

    data.to_csv('./StandardizedCityData/'+city+'_data.csv', index=False)


if __name__ == "__main__":
    directory = './CityData'
    files = Path(directory).glob('*')
    # Loop through all files in the directory to standardize crime types
    for file in files:
        data = pd.read_csv(file)
        
        #Passing data of the file and city name to the function
        standardizeCrimeTypes(data, file.name.split('_')[0])
