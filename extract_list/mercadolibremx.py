# from time import time
import requests
import pandas as pd
import re
from time import sleep
from bs4 import BeautifulSoup
from lxml import html
import random
from utils import *
import math

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
}

search = choose_search()
search = search[:-1]

url_origin = "https://listado.mercadolibre.com.mx/{0}".format(search + "s")

print("Going to... ", url_origin)

response = requests.get(url_origin, headers=headers)

parser = html.fromstring(response.text)

soup = BeautifulSoup(response.text)

total = parser.xpath(
    '//span[@class="ui-search-search-result__quantity-results"]/text()'
)[0]

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = float(str(total_numbers[0]).replace(".", ""))

bypage = 48

print("total of poroducts: ", total)

TOTAL_PAGES = math.ceil(total // bypage)

print("Total of pages: ", TOTAL_PAGES)


def set_link(n):
    if n == 1:
        link_pattern = "https://listado.mercadolibre.com.mx/{}".format(search + "s")
    else:
        link_pattern = (
            "https://listado.mercadolibre.com.mx/{}".format(search + "s")
            + "_Desde_"
            + str(int(49 + (n - 2) * 48))
        )
    return link_pattern


PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

n = 0

titles = []
brands = []
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
                verify=False,
            )
        else:
            response = requests.get(current_url, headers=headers, verify=False)

        parser = html.fromstring(response.text)
        products = parser.xpath(
            '//section[@class="ui-search-results ui-search-results--without-disclaimer"]/ol/li'
        )
        # beautiful soup parser
        soup = BeautifulSoup(response.text)
        products_soup = soup.find_all("li", class_="ui-search-layout__item")

        for index, product in enumerate(products):
            try:
                title = product.xpath(
                    ".//h2[@class='ui-search-item__title ui-search-item__group__element']/text()"
                )[0]
            except:
                title = ""
            try:
                price = product.xpath(
                    './/div[@class="ui-search-price__second-line"]/span[@class="price-tag ui-search-price__part"]/span[@class="price-tag-text-sr-only"]/text()'
                )[0]
            except:
                price = ""
            try:
                oldprice = (
                    product.xpath('.//s/span[@class="price-tag-text-sr-only"]/text()')[
                        0
                    ]
                    .replace("Antes: ", "")
                    .replace(" reais", "")
                )
            except:
                oldprice = ""
            try:
                image = (
                    products_soup[0]
                    .find("img", class_="ui-search-result-image__element")
                    .get("data-src")
                )
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
    df_previous = pd.read_excel("outputs//mercadolibrebr-{}.xlsx".format(search + "s"))
except:
    df_previous = pd.DataFrame()
    pass

if df_previous.empty:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel(
        "outputs//mercadolibremx-{}.xlsx".format(search + "s"), index=False
    )
else:
    df_web.to_excel("outputs//mercadolibremx-{}.xlsx".format(search + "s"), index=False)
