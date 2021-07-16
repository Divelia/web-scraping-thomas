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

url_origin = "https://www.lojadosuplemento.com.br/pesquisa?t={}".format(search.upper())

print("Going to... ", url_origin)

response = requests.get(url_origin, headers=headers)

parser = html.fromstring(response.text)

total = parser.xpath(
    '//div[@class="wrapper text"]//p/strong/text()'
)

total_of_products = get_list_of_numbers(total[0])[0]

bypage = 15

print("total of poroducts: ", total_of_products)

TOTAL_PAGES = math.ceil(total_of_products / bypage)

print("Total of pages: ", TOTAL_PAGES)


def set_link(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = url_origin + "#/pagina-{}".format(n)
    return link_pattern


PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

n = 0

titles = []
prices = []
oldprices = []
images = []
unique_prices = []
lmpm_prices = []

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

        products = parser.xpath("//div[@class='wd-browsing-grid-list   wd-widget-js']/ul/li")

        print(len(products))

        for product in products:
            try:
                title = product.xpath(
                    ".//div[@class='name']/a/text()"
                )[0]
            except:
                title = ""

            try:
                price = (
                    product.xpath(
                        './/div[@class="block-1 savings"]/strong/text()'
                    )
                )[0]
            except:
                price = ""

            try:
                oldprice = product.xpath(
                    './/div[@class="block-1 savings"]/del/text()'
                )[0]
            except:
                oldprice = ""

            try:
                image = product.xpath(
                    './/div[@class="variation variation-root"]/img/@src'
                )[0]
            except Exception as e:
                print(e)
                image = ""

            try:
                unique_price = product.xpath(
                    './/div[@class="block-2 condition"]/span[1]/text()'
                )[0]
            except:
                unique_price = ''

            try:
                lmpm_price = product.xpath(
                    './/div[@class="block-2 condition"]/span[2]/text()'
                ) + product.xpath(
                    './/div[@class="block-2 condition"]/span[3]/text()'
                )
                lmpm_price = ' '.join(lmpm_price)
            except:
                lmpm_price = ''

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            images.append(image)
            unique_prices.append(unique_price)
            lmpm_prices.append(lmpm_price)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "image": image,
                    "unique_price": unique_price,
                    "lmpm_price": lmpm_price
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
dicts["unique_price"] = unique_prices
dicts["lmpm_price"] = lmpm_prices

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//lojadosuplemento-{}.xlsx".format(search))
except:
    df_previous = pd.DataFrame()
    pass

if df_previous.empty:
    df_web.to_excel("outputs//lojadosuplemento-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//lojadosuplemento-{}.xlsx".format(search), index=False)
