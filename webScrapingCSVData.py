from operator import truediv
from select import select
from sodapy import Socrata
from pathlib import Path
from operator import truediv
from select import select
import json
import pandas as pd
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def scrapeMilwaukee(driver):
    driver.find_element(By.XPATH, "//li[contains(@data-id, '395db729-a30a-4e53-ab66-faeb5e1899c8')]/div").click()
    driver.find_element(By.XPATH, "//li[contains(@data-id, '395db729-a30a-4e53-ab66-faeb5e1899c8')]/div/ul/li[2]/").click()

    # cityName="Colombus"
    
    # driver.find_element(By.XPATH, "//input[@placeholder='Enter city, address or coordinates']").send_keys(cityName, Keys.ENTER)

    # driver.find_element(By.XPATH, "//button[@routerlink='/datagrid']").click()


def scrapeData(url):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)

    driver.maximize_window()
    driver.get(url)
    scrapeMilwaukee(driver)


def csvCollect(cityData):

    for i in cityData["collectData"]:
        url=i["url"]
        
        scrapeData(url)

    return 0

if __name__=="__main__":
    # if (len(sys.argv) != 2):
    #     print("please supply the city you want to collect data for")
    #     exit(0)

    # city = Path(sys.argv[1])

    city="Milwaukee"
    f = open('./dataOrganization.json')
    jsonInfo=json.load(f)
    cityData=jsonInfo[city]

    csvCollect(cityData)