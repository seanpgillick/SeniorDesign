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


def defineCrimeType(offense):
    offense = str(offense)
    # Check if Motor Vehicle Theft
    if ("theft" in offense.lower() and ("auto" in offense.lower() or "vehicle" in offense.lower())):
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
    if ("burglary" in offense.lower()):
        return "Burglary"
    # Check if Aggrevated Assault
    if ("assault" in offense.lower() and "ag" in offense.lower()):
        return "Aggrevated Assault"
    # Check if Assault
    if ("assault" in offense.lower()):
        return "Assault"
    # Check if Arson
    if ("arson" in offense.lower()):
        return "Arson"
    # Check if murder
    if ("murder" in offense.lower()):
        return "Murder"
    # Check if Sexual Assault
    if ("assault" in offense.lower() and "sexual" in offense.lower()):
        return "Sexual Assault"

    return offense


def standardizeCrimeTypes(data, city):
    print("Standardizing Crime types for " + city)

    data["offense"] = data['offense'].progress_apply(
        lambda x: defineCrimeType(x))
    print(data)


if __name__ == "__main__":
    directory = './CityData'
    files = Path(directory).glob('*')
    for file in files:
        data = pd.read_csv(file)

        standardizeCrimeTypes(data, file.name.split('_')[0])
