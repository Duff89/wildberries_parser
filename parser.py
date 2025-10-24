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
        basket_ranges = [
            (143, '01'), (287, '02'), (431, '03'), (719, '04'), (1007, '05'),
            (1061, '06'), (1115, '07'), (1169, '08'), (1313, '09'), (1601, '10'),
            (1655, '11'), (1919, '12'), (2045, '13'), (2189, '14'), (2405, '15')
        ]

        for product in item_model.products:
            _short_id = product.id // 100000
            basket = '16'
            for upper_bound, basket_value in basket_ranges:
                if _short_id <= upper_bound:
                    basket = basket_value
                    break
                 
            """Делаем список всех ссылок на изображения и переводим в строку"""
            link_str = "".join([
                f"https://basket-{basket}.wb.ru/vol{_short_id}/part{product.id // 1000}/{product.id}/images/big/{i}.jpg;"
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
