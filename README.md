

# Wildberries parser

Парсит все товары одного бренда с сайта https://www.wildberries.ru/. Сохраняет поля: 'id', 'название', 'цена', 'бренд', 'продаж' и 'рейтинг' в csv файл.

## Youtube (как это работает)

https://youtu.be/mIjIvszqieg

## Установка

Для работы требуется Python 3.5+. Скопируйте проект и установите зависимости:

```bash
  pip install -r requirements.txt
```

## Запуск

Запустите parser.py или вызовите ParseWB("https://www.wildberries.by/catalog?brandpage=27445__MSI").parse() 
Замените на любой другой бренд при необходимости


