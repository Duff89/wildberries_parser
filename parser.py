"""Парсит 'id', 'название', 'цена', 'бренд', 'скидка', 'рейтинг', 'в наличии', 'id продавца' с сайта wildberries, ссылки на изображение"""
import requests
import re
import csv

from models import Items


class ParseWB:
    def __init__(self, url: str):
        self.seller_id = self.__get_seller_id(url)

    @staticmethod
    def __get_item_id(url: str):
        regex = "(?<=catalog/).+(?=/detail)"
        item_id = re.search(regex, url)[0]
        return item_id

    def __get_seller_id(self, url):
        response = requests.get(url=f"https://card.wb.ru/cards/detail?nm={self.__get_item_id(url=url)}")
        seller_id = Items.parse_obj(response.json()["data"])
        return seller_id.products[0].supplierId

    def parse(self):
        _page = 1
        self.__create_csv()
        while True:
            response = requests.get(
                f'https://catalog.wb.ru/sellers/catalog?dest=-1257786&supplier={self.seller_id}&page={_page}',
            )
            _page += 1
            items_info = Items.parse_obj(response.json()["data"])
            if not items_info.products:
                break
            self.__get_images(items_info)
            self.__save_csv(items_info)

    def __create_csv(self):
        with open("wb_data.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ['id', 'название', 'цена', 'бренд', 'скидка', 'рейтинг', 'в наличии', 'id продавца', 'изображения'])

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
                                 product.volume,
                                 product.supplierId,
                                 product.image_links
                                 ])

    def __get_images(self, item_model: Items):
        for product in item_model.products:
            _shot_id = product.id // 100000
            for product in item_model.products:
                _short_id = product.id // 100000
                """Используем match/case для определения basket на основе _short_id"""
                basket = match(_short_id,
                    (range(0, 144), '01'),       # Если _short_id находится в диапазоне от 0 до 143, присвоить '01'
                    (range(144, 288), '02'),     # И так далее для остальных диапазонов
                    (range(288, 432), '03'),     
                    (range(432, 720), '04'),
                    (range(720, 1008), '05'),
                    (range(1008, 1062), '06'),
                    (range(1062, 1116), '07'),
                    (range(1116, 1170), '08'),
                    (range(1170, 1314), '09'),
                    (range(1314, 1602), '10'),
                    (range(1602, 1656), '11'),
                    (range(1656, 1920), '12'),
                    ('13')                      # Если _short_id не входит ни в один из предыдущих диапазонов, присвоить '13' basket-у
                )
                url = f"https://basket-{basket}.wb.ru/vol{_shot_id}/part{product.id // 1000}/{product.id}/images/big/1.jpg"
                res = requests.get(url=url)
                if res.status_code == 200:
                    """Делаем список всех ссылок на изображения и переводим в строку"""
                    link_str = "".join([
                                           f"https://basket-{basket}.wb.ru/vol{_shot_id}/part{product.id // 1000}/{product.id}/images/big/{i}.jpg;"
                                           for i in range(1, product.pics + 1)])
                    product.image_links = link_str
                    link_str = ''


if __name__ == "__main__":
    ParseWB("https://www.wildberries.ru/catalog/160228771/detail.aspx").parse()
