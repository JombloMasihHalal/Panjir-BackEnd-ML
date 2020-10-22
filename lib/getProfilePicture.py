import os
import selenium
from selenium import webdriver
import time
from PIL import Image
import io
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import ElementClickInterceptedException

def getProfilePicture(username):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    link = "https://twitter.com/"+ username + "/photo"
    driver.get(link)
    driver.implicitly_wait(4)
    res = [e.get_attribute("src") for e in driver.find_elements_by_tag_name('img')]
    driver.close()
    return None if len(res)==0 else res[0]
