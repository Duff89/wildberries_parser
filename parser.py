"""Парсит 'id', 'название', 'цена', 'бренд', 'скидка', 'рейтинг', 'в наличии', 'id продавца' с сайта wildberries,
 ссылки на изображение, количество отзывов и рейтинг"""
import requests
import re
import csv

from models import Items, Feedback


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
        seller_id = Items.model_validate(response.json()["data"])
        return seller_id.products[0].supplierId

    def parse(self):
        _page = 1
        self.__create_csv()
        while True:
            response = requests.get(
                f'https://catalog.wb.ru/sellers/catalog?dest=-1257786&supplier={self.seller_id}&page={_page}',
            )
            _page += 1
            items_info = Items.model_validate(response.json()["data"])
            if not items_info.products:
                break
            self.__get_images(items_info)
            self.__feedback(items_info)
            self.__save_csv(items_info)

    @staticmethod
    def __create_csv():
        with open("wb_data.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ['id', 'название', 'цена', 'бренд', 'скидка', 'рейтинг', 'в наличии', 'id продавца', 'изображения',
                 "отзывы с текстом", "рейтинг"])

    @staticmethod
    def __save_csv(items: Items):
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
                                 product.image_links,
                                 product.feedback_count,
                                 product.valuation
                                 ])

    @staticmethod
    def __get_images(item_model: Items):
        for product in item_model.products:
            _shot_id = product.id // 100000
            for product in item_model.products:
                _short_id = product.id // 100000
                """Используем match/case для определения basket на основе _short_id"""
                if 0 <= _short_id <= 143:
                    basket = '01'
                elif 144 <= _short_id <= 287:
                    basket = '02'
                elif 288 <= _short_id <= 431:
                    basket = '03'
                elif 432 <= _short_id <= 719:
                    basket = '04'
                elif 720 <= _short_id <= 1007:
                    basket = '05'
                elif 1008 <= _short_id <= 1061:
                    basket = '06'
                elif 1062 <= _short_id <= 1115:
                    basket = '07'
                elif 1116 <= _short_id <= 1169:
                    basket = '08'
                elif 1170 <= _short_id <= 1313:
                    basket = '09'
                elif 1314 <= _short_id <= 1601:
                    basket = '10'
                elif 1602 <= _short_id <= 1655:
                    basket = '11'
                elif 1656 <= _short_id <= 1919:
                    basket = '12'
                else:
                    basket = '13'
                url = f"https://basket-{basket}.wb.ru/vol{_shot_id}/part{product.id // 1000}/{product.id}/images/big/1.jpg"
                res = requests.get(url=url)
                if res.status_code == 200:
                    """Делаем список всех ссылок на изображения и переводим в строку"""
                    link_str = "".join([
                        f"https://basket-{basket}.wb.ru/vol{_shot_id}/part{product.id // 1000}/{product.id}/images/big/{i}.jpg;"
                        for i in range(1, product.pics + 1)])
                    product.image_links = link_str
                    link_str = ''

    @staticmethod
    def __feedback(item_model: Items):
        for product in item_model.products:
            url = f"https://feedbacks1.wb.ru/feedbacks/v1/{product.root}"
            res = requests.get(url=url)
            if res.status_code == 200:
                feedback = Feedback.model_validate(res.json())
                product.feedback_count = feedback.feedbackCountWithText
                product.valuation = feedback.valuation


if __name__ == "__main__":
    ParseWB("https://www.wildberries.ru/catalog/141217830/detail.aspx").parse()
