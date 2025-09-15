import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import FILENAME_CSV, FILENAME_EXCEL


def read_excel(FILENAME_EXCEL):
    df = pd.read_excel(FILENAME_EXCEL, engine="openpyxl", header=None)
    first_col = df.iloc[:, 0]
    values_list = [
        None if pd.isna(x) else (x.strip() if isinstance(x, str) else x)
        for x in first_col.tolist()
    ]
    return values_list


def get_html_code_from_url(parsing_url, number_header):
    if number_header == 1:
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,be;q=0.6",
        }
    else:
        default_headers = {}

    try:
        response = requests.get(parsing_url, headers=default_headers)
        # Используйте requests.get для простоты
        response.raise_for_status()  # Проверка для HTTP ошибок (например, 404, 500 и т.д.)
        x = response.text  # Получаем JSON ответ от сервера
        return x
    except requests.exceptions.HTTPError as http_err:
        logging.exception(
            f"HTTP error occurred: {http_err}"
        )  # Вывод ошибки для отладки
    except Exception as err:
        logging.exception(f"An error occurred: {err}")  # Общая обработка исключений


def write_csv(FILENAME_CSV):
    return FILENAME_CSV


def parsing_toolsby(parsing_url):
    product_title = None
    product_image_url = None
    product_price = None
    product_article = None

    html_code = get_html_code_from_url(parsing_url, 1)

    soup = BeautifulSoup(html_code, "html.parser")

    # meta og:title -> product_title
    meta_title = soup.select_one('meta[property="og:title"]')
    product_title = (
        meta_title.get("content")
        if meta_title and meta_title.has_attr("content")
        else None
    )

    # meta og:image -> product_image_url
    meta_image = soup.select_one('meta[property="og:image"]')
    product_image_url = (
        meta_image.get("content")
        if meta_image
        and meta_image.has_attr("content")
        and meta_image.get("content") != ""
        else None
    )
    # артикул
    el = soup.select_one("#product_artikul")
    product_article = "toolsby_" + el.get_text(strip=True) if el else None
    # цена
    el = soup.select_one(".product-parameter__price-value")
    if not el:
        return None
    product_price_str = el.get_text(strip=True) if el else None
    product_price_str_replase = product_price_str.replace(",", ".")
    product_price = (
        float(product_price_str_replase) if product_price_str_replase else None
    )

    result = [
        product_title,
        product_image_url,
        product_article,
        product_price,
    ]
    return result


def list_traversal():
    a1 = []
    a2 = []
    a3 = []
    a4 = []
    parsing_url_list = read_excel(FILENAME_EXCEL)
    for parsing_url in parsing_url_list:
        a1a2a3a4 = parsing_toolsby(parsing_url)
        a1.append(a1a2a3a4[2])
        a2.append(a1a2a3a4[0])
        a3.append(a1a2a3a4[1])
        a4.append(a1a2a3a4[3])

    data = {
        "product_article": a1,
        "product_title": a2,
        "product_image_url": a3,
        "product_price": a4,
    }
    df = pd.DataFrame(data)
    df.to_csv(FILENAME_CSV, encoding="cp1251")


logging.basicConfig(
    level=logging.WARNING,
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)




list_traversal()
