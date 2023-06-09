

# Wildberries parser

Парсит все товары продавца с сайта https://www.wildberries.ru/. Сохраняет поля: 'id', 'название', 'цена', 'бренд', 'скидка', 'рейтинг', 'id продаца' в csv файл.

## Youtube (как это работает)

https://youtu.be/mIjIvszqieg (часть 1: парсим товары одного бренда)
https://youtu.be/k3P4lrzzxnI (часть 2: парсим товары одного продавца)

## Установка

Для работы требуется Python 3.5+. Скопируйте проект и установите зависимости:

```bash
  pip install -r requirements.txt
```

## Запуск

Запустите parser.py или вызовите ParseWB("https://www.wildberries.ru/catalog/27605639/detail.aspx").parse() 
Замените на любой другой товар при необходимости


