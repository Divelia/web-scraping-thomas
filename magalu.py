from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
import random

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

# URL origin
driver.get("https://www.magazineluiza.com.br/busca/vitaminas/")

# get the total of results
total = driver.find_element(By.XPATH, '//h1[@itemprop="description"]/small').text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = total_numbers[0]

bypage = 60

print("total of poroducts: ", total)

if total % bypage == 0:
    TOTAL_PAGES = int(total // bypage)
else:
    TOTAL_PAGES = int(total // bypage + 1)

print("Total of pages: ", TOTAL_PAGES)

titles = []
prices = []
oldprices = []
brands = []
ids = []
sellbys = []
images = []


def set_link(n):
    if n == 1:
        link_pattern = "https://www.magazineluiza.com.br/busca/vitaminas/"
    else:
        link_pattern = (
            "https://www.magazineluiza.com.br/busca/vitaminas/"
            + str(int(n))
        )
    return link_pattern


# set pagination rules
PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))


# Mientras la pagina en la que me encuentre, sea menor que la maxima pagina que voy a sacar... sigo ejecutando...
while PAGINACION_HASTA >= PAGINACION_DESDE:

    current_link = set_link(PAGINACION_DESDE)
    print("START WITH: ", current_link)

    driver.get(current_link)

    # links_products = driver.find_element_by_xpath('//section[@class="ui-search-results ui-search-results--without-disclaimer"]//ol/li//a[@class="ui-search-result__content ui-search-link"]')

    time.sleep(random.uniform(1.0, 5.0))

    links_products = driver.find_elements(
        By.XPATH,
        '//ul[@class="productShowCase big"]/li/a[@itemprop="url"]',
    )

    print("Total of producst link: ", len(links_products))

    links_de_la_pagina = []

    for a_link in links_products:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    for link in links_de_la_pagina:

        try:
            # Voy a cada uno de los links de los detalles de los productos
            driver.get(link)
            try:
                title = (
                    driver.find_element(
                        By.XPATH, '//h1[@class="header-product__title"]'
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                title = ""

            try:
                price_list = driver.find_elements(
                    By.XPATH,
                    '//div[@class="price-template-price-block"]/span',
                )
                price = price_list[1].text.replace("\n", "").replace("\t", "")
            except:
                price = ""

            try:
                oldprice = (
                    driver.find_element(
                        By.XPATH,
                        '//div[@class="price-template"]/div[@class="price-template__from"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                oldprice = ""

            try:
                brand = (
                    driver.find_element(
                        By.XPATH,
                        '//small[@class="header-product__code"]/a[@class="header-product__text-interation"]/span',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                brand = ""

            try:
                sellby = (
                    driver.find_element(
                        By.XPATH,
                        '//button[@class="seller-info-button js-seller-modal-button"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                sellby = ""

            try:
                id_list = driver.find_elements(
                    By.XPATH, '//small[@class="header-product__code"]'
                )
                id = id_list[0].text.replace("\n", "").replace("\t", "")
            except:
                id = ""

            try:
                image = driver.find_element(
                    By.XPATH,
                    '//img[@class="showcase-product__big-img js-showcase-big-img ls-is-cached lazyloaded"]',
                ).get_attribute("src")
            except:
                image = ""

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            brands.append(brand)
            ids.append(id)
            sellbys.append(sellby)
            images.append(image)

            # following data extracted

            print(
                "Item: ",
                {
                    "id": id,
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "brand": brand,
                    "sellby": sellby,
                    "image": image,
                },
            )

            driver.back()
        except Exception as e:
            print(e)
            driver.back()

    PAGINACION_DESDE += 1

dicts = {}

dicts["id"] = ids
dicts["name"] = titles
dicts["brand"] = brands
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["sellby"] = sellbys
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)
try:
    df_previous = pd.read_excel("outputs//magalu.xlsx")
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//magalu.xlsx", index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//magalu.xlsx", index=False)
