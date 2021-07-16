# from time import time
import re
import random
import requests
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from lxml import html
from utils import *
import math

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
}

search = choose_search()

url_origin = "https://www.mundoverde.com.br/{0}?_q={1}&map=ft".format(search, search.upper())

print("Going to... ", url_origin)

response = requests.get(url_origin, headers=headers)

parser = html.fromstring(response.text)

try:
    total = parser.xpath(
        '//div[contains(@class, "t-action--small")]/span/text()'
    )

    total_of_products = get_list_of_numbers(total)
    bypage = 12
    print("total of poroducts: ", total_of_products)

    TOTAL_PAGES = math.ceil(total_of_products / bypage)

    print("Total of pages: ", TOTAL_PAGES)
except:
    pass

print(total)


def set_link(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = "https://www.mundoverde.com.br/{0}?_q={1}&map=ft".format(search, search.upper()) + "&page={}".format(n)
    return link_pattern


PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

n = 0

titles = []
prices = []
oldprices = []
images = []

error = False

while PAGINACION_HASTA >= PAGINACION_DESDE:

    print("Start page number {}".format(PAGINACION_DESDE))

    # randomize requests
    sleep(random.uniform(1.0, 3.0))

    try:
        current_url = set_link(PAGINACION_DESDE)
        print("Going to... ", current_url)

        # requests parser
        if error:
            current_proxy = generate_free_proxy()
            response = requests.get(
                current_url,
                headers=headers,
                proxies={
                    "http": "http://" + str(current_proxy),
                    "https": "https://" + str(current_proxy),
                    "ftp": "ftp://" + str(current_proxy),
                },
            )
        else:
            response = requests.get(current_url, headers=headers)

        parser = html.fromstring(response.text)
        products = parser.xpath("//div[contains(@class, 'vtex-search-result-3-x-gallery')]/div/text()")
        print(products)
        # beautiful soup parser
        # soup = BeautifulSoup(response.text)
        # products_soup = soup.find_all('div', class_="ui-search-layout__item")

        for index, product in enumerate(products):
            try:
                title = product.xpath(
                    './/span[@class="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]/text()'
                )[0]
            except:
                title = ""
            try:
                price = (
                    product.xpath(
                        './/div[@class="vtex-store-components-3-x-sellingPrice vtex-store-components-3-x-sellingPriceContainer vtex-product-summary-2-x-sellingPriceContainer pt1 pb3 c-on-base vtex-product-summary-2-x-price_sellingPriceContainer"]//span[@class="vtex-product-summary-2-x-currencyContainer"]/text()'
                    )[0]
                )
            except:
                price = ""
            try:
                oldprice = product.xpath(
                    './/div[@class="vtex-store-components-3-x-listPrice vtex-product-summary-2-x-listPriceContainer pv1 normal c-muted-2 vtex-product-summary-2-x-price_listPriceContainer"]//span[@class="vtex-product-summary-2-x-currencyContainer"]/text()'
                )[0]
            except:
                oldprice = ""
            try:
                image = product.xpath(
                    './/img[@class="vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image"]/@src'
                )[0]
            except Exception as e:
                print(e)
                image = ""

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            images.append(image)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "image": image,
                },
            )

        PAGINACION_DESDE += 1
        print("Finish page number {}".format(PAGINACION_DESDE))
        n += 1
        if PAGINACION_DESDE > PAGINACION_HASTA:
            print("Scraper finished")
            break

        print("PAGINACION_DESDE: ", PAGINACION_DESDE, " ", int(PAGINACION_DESDE))
        print("PAGINACION_HASTA: ", PAGINACION_HASTA, " ", int(PAGINACION_HASTA))

    except Exception as e:
        print(e)
        error = True
        print("cant access to link")

        continue

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//mundoverde-{}.xlsx".format(search))
except:
    df_previous = pd.DataFrame()
    pass

if df_previous.empty:
    df_web.to_excel("outputs//mundoverde-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//mundoverde-{}.xlsx".format(search), index=False)
