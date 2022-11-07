from operator import truediv
from select import select
import sys
import pandas as pd
from sodapy import Socrata
import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def buttonClick():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    url = "https://communitycrimemap.com/"
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)

    driver.maximize_window()
    driver.get(url)
    driver.find_element(By.XPATH, "//button[contains(@class, 'mat-focus-indicator btn-hp-25 mat-flat-button mat-button-base mat-primary')]").click()

    cityName="Colombus"
    
    driver.find_element(By.XPATH, "//input[@placeholder='Enter city, address or coordinates']").send_keys(cityName, Keys.ENTER)

    driver.find_element(By.XPATH, "//button[@routerlink='/datagrid']").click()

    firstRun=True
    rows=[]
    x=0
    while(x<5):
        if(firstRun):
            time.sleep(10)
            firstRun=False
        else:
            time.sleep(2)
        newRow=(driver.find_elements(By.TAG_NAME, "tr"))
        for row in newRow:
            textInfo = row.find_elements(By.TAG_NAME, "td")
            print(textInfo)
        newRow.pop(51)
        newRow.pop(0)
        rows.extend(newRow)
        driver.find_element(By.XPATH, "//button[contains(@class, 'mat-focus-indicator mat-tooltip-trigger mat-paginator-navigation-next mat-icon-button mat-button-base')]").click()
        # l = driver.find_elements("//*[@id='cdk-drop-list-3']/tbody/tr")
        
        print(len(rows))
        x+=1
    

    return 0

buttonClick()
# scrapeData()