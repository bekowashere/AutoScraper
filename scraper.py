import json
import os
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from helpers import toFolderName, slugify

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


class BrandScraper:
    def __init__(self):
        self.baseurl: str = "https://www.autoevolution.com/cars/"
        self.folder_name: str = "all_brand_data.json"
        self.html_element = {'itemtype': 'https://schema.org/Brand'}
        self.brand_data: list = []

    def collect_data(self):
        # prepare
        driver.get(self.baseurl)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # find brand elements
        elements = soup.find_all('div', self.html_element)

        for element in elements:
            brand_name = element.find('span', itemprop="name").get_text()
            brand_detail_url = element.find('a')['href']
            brand_image_url = element.find('img')['src']

            # Slug
            http_text, _brand_slug = brand_detail_url.split('.com/')
            brand_slug = _brand_slug.replace('/', '')

            brand_image_path = f'{toFolderName(brand_name)}.jpg'

            # Edit brand_name (space)
            brand_new_name = brand_name.strip()

            new_brand = {
                "brand_name": brand_new_name,
                "brand_detail_url": brand_detail_url,
                "brand_slug": brand_slug,
                "brand_description": "",
                "brand_image_url": brand_image_url,
                "brand_image_path": brand_image_path
            }

            self.brand_data.append(new_brand)

        print("All car data collected.")
        driver.close()


brand = BrandScraper()
brand.collect_data()
print(brand.brand_data)
