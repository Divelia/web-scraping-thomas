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

url_origin = "https://supernaturista.com/search?type=article%2Cpage%2Cproduct&q={}*".format(search + "s")

print("Going to... ", url_origin)

response = requests.get(url_origin, headers=headers)

parser = html.fromstring(response.text)

# soup = BeautifulSoup(response.text)

total = parser.xpath(
    '//nav[@class="breadcrumbs-container"]/span[2]/text()'
)[0]

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = float(str(total_numbers[0]).replace(".", ""))

bypage = 24

print("total of products: ", total)

TOTAL_PAGES = math.ceil(total // bypage)

print("Total of pages: ", TOTAL_PAGES)


def set_link(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = (
            "https://supernaturista.com/search?page={0}&q={1}%2A&type=article%2Cpage%2Cproduct".format(n, search + "s")
        )
    return link_pattern


# PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
# PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

n = 0

titles = []
brands = []
prices = []
oldprices = []
images = []
hyperlinks = []

error = False

n = 1
while True:

    # print("Start page number {}".format(PAGINACION_DESDE))

    # randomize requests
    sleep(random.uniform(2.0, 4.0))

    try:
        print('AAAAAAAAAAA')
        current_url = set_link(1)
        print("Going to... ", current_url)

        if n == 1:
            # requests parser
            if error:
                current_proxy = generate_free_proxy()
                response = requests.get(
                    current_url,
                    headers=headers,
                    proxies={
                        # "http": "http://" + str(current_proxy),
                        "https": "https://" + str(current_proxy),
                        # "ftp": "ftp://" + str(current_proxy),
                    },
                    verify=False,
                )
            else:
                response = requests.get(current_url, headers=headers, verify=False)
        else:
            print('getting ', "https://supernaturista.com" + nextpage)
            response = requests.get("https://supernaturista.com" + nextpage, headers=headers, verify=False)

        parser = html.fromstring(response.text)
        products = parser.xpath(
            '//ul[@class="productgrid--items products-per-row-3"]/li'
        )

        for product in products:
            try:
                title = product.xpath(
                    ".//h2[@class='productitem--title']/a/text()"
                )[0].replace('\n', ' ').replace('\r', ' ').strip()
            except:
                title = ""

            try:
                price = product.xpath(
                    './/div[@class="price--main"]/span[@class="money"]/text()'
                )[0].replace('\n', ' ').replace('\r', ' ').strip()
            except:
                price = ""

            try:
                brand = product.xpath(
                    './/span[@class="productitem--vendor"]/a/text()'
                )[0].replace('\n', ' ').replace('\r', ' ').strip()
            except:
                brand = ""

            try:
                oldprice = (
                    product.xpath('.//div[@class="price--compare-at visible"]/span[@class="money"]/text()')[0]
                    .replace('\n', ' ').replace('\r', ' ').strip()
                )
            except:
                oldprice = ""

            try:
                image = product.xpath('.//img[@class="productitem--image-primary"]/@src')[0]
            except Exception as e:
                print(e)
                image = ""

            try:
                hyperlink = 'https://supernaturista.com' + product.xpath('.//a[@class="productitem--image-link"]/@href')[0]
            except Exception as e:
                print(e)
                hyperlink = ""

            titles.append(title)
            prices.append(price)
            brands.append(brand)
            oldprices.append(oldprice)
            images.append(image)
            hyperlinks.append(hyperlink)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "image": image,
                    "brand": brand,
                    "hyperlink": hyperlink
                },
            )

        n += 1
        # PAGINACION_DESDE += 1
        #
        # print("Finish page number {}".format(PAGINACION_DESDE))
        # n += 1
        # if PAGINACION_DESDE > PAGINACION_HASTA:
        #     print("Scraper finished")
        #     break
        #
        # print("PAGINACION_DESDE: ", PAGINACION_DESDE, " ", int(PAGINACION_DESDE))
        # print("PAGINACION_HASTA: ", PAGINACION_HASTA, " ", int(PAGINACION_HASTA))

        try:
            nextpage = parser.xpath('//a[@aria-label="Go to next page"]/@href')[0]
        except:
            break

    except Exception as e:
        print(e)
        error = True
        print("cant access to link")

        continue

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["brand"] = brands
dicts["oldprice"] = oldprices
dicts["image"] = images
dicts["hyperlink"] = hyperlinks

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//supernaturista-{}.xlsx".format(search + "s"))
except:
    df_previous = pd.DataFrame()
    pass

if df_previous.empty:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel(
        "outputs//supernaturista-{}.xlsx".format(search + "s"), index=False
    )
else:
    df_web.to_excel("outputs//supernaturista-{}.xlsx".format(search + "s"), index=False)
