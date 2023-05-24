"""Парсит 'id', 'название', 'цена', 'бренд', 'продаж', 'рейтинг', 'в наличии' с сайта wildberries"""
import requests
import re
import csv

from models import Items


class ParseWB:
    def __init__(self, url: str):
        self.brand_id = self.__get_brand_id(url)

    @staticmethod
    def __get_brand_id(url: str):
        regex = "(?<=brandpage=).+(?=__)"
        brand_id = re.search(regex, url)[0]
        return brand_id

    def parse(self):
        i = 1
        self.__create_csv()
        while True:
            response = requests.get(
                f'https://catalog.wb.ru/brands/m/catalog?brand={self.brand_id}&limit=300&sort=popular&page={i}&appType=128&curr=rub&locale=by&lang=ru&dest=-59208&regions=1,4,22,30,31,33,40,48,66,68,69,70,80,83,114,115&reg=1&spp=0',
            )
            i += 1
            items_info = Items.parse_obj(response.json()["data"])
            if not items_info.products:
                break
            self.__save_csv(items_info)

    def __create_csv(self):
        with open("wb_data.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'название', 'цена', 'бренд', 'продаж', 'рейтинг', 'в наличии'])

    def __save_csv(self, items):
        with open("wb_data.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            for product in items.products:
                writer.writerow([product.id,
                                 product.name,
                                 product.salePriceU,
                                 product.brand,
                                 product.sale,
                                 product.rating,
                                 product.volume])


if __name__ == "__main__":
    ParseWB("https://www.wildberries.by/catalog?brandpage=27445__MSI").parse()
