import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from loguru import logger
import time
import cv2
import os


class DomPics:
    def __init__(self):
        self.banks = None
        CHROME_BIN_LOCATION = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        CHROME_DRIVER_LOCATION = r'C:\Users\Lenovo\Downloads\chromedriver.exe'
        USER_DATA_DIR = r'C:\environments\selenium'

        options = selenium.webdriver.chrome.options.Options()
        service = selenium.webdriver.chrome.service.Service(CHROME_DRIVER_LOCATION)
        options.add_argument(f'user-data-dir={USER_DATA_DIR}')
        options.add_argument('--disable-popup-blocking')
        options.binary_location = CHROME_BIN_LOCATION
        self.driver = selenium.webdriver.Chrome(options=options, service=service)
        self.driver.maximize_window()

    def close(self):
        self.driver.close()

    def get_obj_pg(self, obj):
        url = fr'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82/{obj}'
        self.driver.get(url)

    def slide(self):
        src = self.driver.find_element(By.XPATH, "//body").get_attribute('outerHTML')

        XPATH = r'/html/body/div[2]/div[2]/div[1]/div/div/div[2]/div/div[4]/div[2]/div/div[3]'
        el = self.driver.find_element(By.XPATH, XPATH)
        self.driver.execute_script('arguments[0].scrollIntoView();', el)
        soup = bs(src)

        regex = re.compile('slick-track.*')
        ls = len(soup.find_all('div', {'class': regex})[0].contents)

        st = time.time()
        res = []
        i = 1
        time.sleep(5)
        while True:
            el = obj.driver.find_element(By.XPATH,
                                         f"/html/body/div[2]/div[2]/div[1]/div/div/div[2]/div/div[4]/div[2]/div/div[2]/div/div[{i}]/div/div/div/button")
            XPATH = r'/html/body/div[2]/div[2]/div[1]/div/div/div[2]/div/div[4]/div[2]/div/div[3]'
            el1 = obj.driver.find_element(By.XPATH, XPATH)

            el.click()
            time.sleep(5)
            el1.click()

            i += 1


    def button_clicker(self):
        i = 1
        while True:
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                f"/html/body/div[2]/div[2]/div[1]/div/div/div[2]/div/div[4]/div[2]/div/div[2]/div/div[{i}]/div/div/div/button")))

                el.click()
                i += 1
            except:
                break

    # def
    #     src = self.driver.find_element(By.XPATH, "//body").get_attribute('outerHTML')
    #
    #     soup = bs(src)
    #     regex = re.compile('card_wrapper.*')
    #     ls = soup.find_all('div', {'class': regex})


obj = DomPics()
obj.get_obj_pg(46773)
page = obj.slide()
image_tags = page.find_all('img')
res += [img['src'] for img in image_tags]

el = obj.driver.find_element(By.XPATH,
                             f"/html/body/div[2]/div[2]/div[1]/div/div/div[2]/div/div[4]/div[2]/div/div[2]/div/div[{2}]/div/div/div/button")
XPATH = r'/html/body/div[2]/div[2]/div[1]/div/div/div[2]/div/div[4]/div[2]/div/div[3]'
el1 = obj.driver.find_element(By.XPATH, XPATH)

el.click()
el1.click()
