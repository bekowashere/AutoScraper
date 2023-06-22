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
    def __init__(
            self,
            base_url: str = "https://www.autoevolution.com/cars/",
            folder_name: str = "all_brand_data.json",
            brand_data: list = None,
            soup_elements: dict = None
    ):

        self.base_url = base_url
        self.folder_name = folder_name

        if brand_data is None:
            self.brand_data = []
        else:
            self.brand_data = brand_data

        if soup_elements is None:
            self.soup_elements = {
                "tag": "div",
                "key": "itemtype",
                "value": "https://schema.org/Brand"
            }
        else:
            self.soup_elements = soup_elements

        self.html_element = {self.soup_elements["key"]: self.soup_elements["value"]}

    def collect_data(self):
        # prepare
        driver.get(self.base_url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # find brand elements
        elements = soup.find_all(self.soup_elements["tag"], self.html_element)

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

        print("All cars data collected.")
        driver.close()

    def create_json(self):
        with open(self.folder_name, 'w') as f:
            json.dump(self.brand_data, f, indent=2)

        print(f"{self.folder_name} successfully created")

    def create_images(self):
        # open folder
        with open(self.folder_name, 'r', encoding="UTF-8") as f:
            data = json.load(f)

        # inside folder
        os.chdir(os.path.join(os.getcwd(), 'images'))

        for obj in data:
            f_name = toFolderName(obj["brand_name"])
            try:
                os.mkdir(os.path.join(os.getcwd(), f_name))
            except OSError as e:
                print(e)

            os.chdir(os.path.join(os.getcwd(), f_name))

            with open(obj["brand_image_path"], 'wb') as f:
                b_im = requests.get(obj["brand_image_url"])
                f.write(b_im.content)

            os.chdir('..')

        print("Brand Images successfully created")

        # exit folder
        os.chdir('..')


class SeriesScraper:
    def __init__(
            self,
            folder_name: str = "all_series_data.json ",
            series_data: list = None,
            soup_elements: dict = None
    ):

        self.folder_name = folder_name

        if series_data is None:
            self.series_data = []
        else:
            self.series_data = series_data

        if soup_elements is None:
            self.soup_elements = {
                "tag": "div",
                "key": "class",
                "value": "carmod"
            }
        else:
            self.soup_elements = soup_elements

        self.html_element = {self.soup_elements["key"]: self.soup_elements["value"]}

    def __get_brand_data(self, f_name: str):
        with open(f_name, 'r', encoding="UTF-8") as f:
            brands_data = json.load(f)

        return brands_data

    def __save_series(self, brand_name: str, brand_detail_url: str, brand_slug: str, series_elements):
        for s in series_elements:
            series_brand_name = brand_name
            series_title = s.find('h4').get_text()
            series_name = series_title.replace(series_brand_name, "").strip()
            series_detail_url = s.find('a')['href']

            series_image = s.find('img')
            series_image_url = s.find('img')['src']
            series_image_path = f"{toFolderName(series_name)}.jpg"

            # Slug
            domain, _slug_series = series_detail_url.split(f"/{brand_slug}/")
            series_slug = _slug_series.replace('/', '').strip()

            # Body Style
            try:
                body_style = s.find('p', class_=["body"]).get_text().upper()
            except AttributeError:
                body_style = None

            # Continue
            is_discontinued = False
            series_generation_count = None

            if series_image.has_attr('class'):
                if series_image.attrs['class'][0] == 'faded':
                    is_discontinued = True
                    # Generation Count
                    try:
                        series_generation_count = s.find('b', {'class': 'col-red'}).text
                    except AttributeError:
                        series_generation_count = None
            else:
                # Generation Count
                try:
                    series_generation_count = s.find('b', {'class': 'col-green2'}).text
                except AttributeError:
                    series_generation_count = None

            # Fuel Types
            series_fuel_types = []
            fuel_element = s.find('p', {'class': 'eng'})
            fuels = fuel_element.find_all('span')
            for fuel in fuels:
                fuel_text = fuel.text.title()
                series_fuel_types.append(fuel_text)

            series = {
                "brand_name": series_brand_name,
                "brand_detail_url": brand_detail_url,
                "brand_slug": brand_slug,
                "series_name": series_name,
                "series_detail_url": series_detail_url,
                "series_slug": series_slug,
                "series_bodyStyle": body_style,
                "series_isDiscontinued": is_discontinued,
                "series_image_url": series_image_url,
                "series_image_path": series_image_path,
                "series_fuelType": series_fuel_types,
                "series_generation_count": series_generation_count
            }

            self.series_data.append(series)

    def collect_data(self, brand_folder_name: str = "all_brand_data.json"):
        brands_data = self.__get_brand_data(brand_folder_name)

        for _brand in brands_data:
            brand_name = _brand["brand_name"]
            brand_detail_url = _brand["brand_detail_url"]
            brand_slug = _brand["brand_slug"]

            time.sleep(1)
            driver.get(brand_detail_url)
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(1)

            elements = soup.find_all(self.soup_elements["tag"], self.html_element)

            self.__save_series(brand_name, brand_detail_url, brand_slug, elements)

        print("All series data collected")
        driver.close()

    def create_json(self):
        with open(self.folder_name, 'w') as f:
            json.dump(self.series_data, f, indent=2)

        print(f"{self.folder_name} successfully created")

    def create_images(self):
        with open(self.folder_name, 'r', encoding="UTF-8") as f:
            data = json.load(f)

        os.chdir(os.path.join(os.getcwd(), 'images'))

        for obj in data:
            brand_folder_name = toFolderName(obj["brand_name"])
            os.chdir(os.path.join(os.getcwd(), brand_folder_name))

            series_folder_name = toFolderName(obj["series_name"])
            series_image_path = f"{series_folder_name}.jpg"
            os.mkdir(os.path.join(os.getcwd(), series_folder_name))
            os.chdir(os.path.join(os.getcwd(), series_folder_name))
            with open(series_image_path, 'wb') as f:
                s_im = requests.get(obj["series_image_url"])
                f.write(s_im.content)

            os.chdir('..')
            os.chdir('..')

        os.chdir('..')
