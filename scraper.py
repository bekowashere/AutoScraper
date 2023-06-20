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
        self.html_element = {'itemtype': 'https://schema.org/Brand'}
        self.folder_name: str = "all_brand_data.json"
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

    def create_json(self):
        with open(self.folder_name, 'w') as f:
            json.dump(self.brand_data, f, indent=2)

        print(f"{self.folder_name} successfully created")

    def create_images(self):
        # open folder
        with open(self.folder_name, 'r', encoding="UTF-8") as f:
            data = json.load(f)

        # inside brand_logo folder
        os.chdir(os.path.join(os.getcwd(), 'brand_logo'))

        for obj in data:
            with open(obj["brand_image_path"], 'wb') as f:
                b_im = requests.get(obj["brand_image_url"])
                f.write(b_im.content)

        print("Brand Images successfully created")

        # exit folder
        os.chdir('..')


brand = BrandScraper()
brand.collect_data()
brand.create_json()
brand.create_images()
