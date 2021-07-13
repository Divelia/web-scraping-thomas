from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import math
import re
from tqdm import tqdm
import random
import pandas as pd

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()
opts.add_argument("user-agent=" + list_agents[0])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)


def set_url(n):
    if n == 1:
        return "https://www.natue.com.br/suplementos"
    else:
        return "https://www.natue.com.br/suplementos?page={}".format(n)


# URL origin
url_origin = "https://www.natue.com.br/suplementos"

driver.get(url_origin)

total_products_string = driver.find_element(
    By.XPATH,
    '//div[@class="vtex-search-result-3-x-totalProducts--layout pv5 ph9 bn-ns bt-s b--muted-5 tc-s tl t-action--small"]/span',
).text

bypage = 12
total_products = [
    float(s) for s in re.findall(r"-?\d+\.?\d*", total_products_string.replace(",", ""))
][0]

print("total of products  ", total_products, " by page: ", bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of pages ", total_of_pages)

total_links = []


PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

ids = []
titles = []
prices = []
oldprices = []
categories = []
images = []

while PAGINA_FIN >= PAGINA_INICIO:

    print(set_url(PAGINA_INICIO))
    driver.get(set_url(PAGINA_INICIO))


    links_productos = driver.find_elements(
        By.XPATH,
        '//section[@class="vtex-product-summary-2-x-container vtex-product-summary-2-x-containerNormal overflow-hidden br3 h-100 w-100 flex flex-column justify-between center tc"]//a[@class="vtex-product-summary-2-x-clearLink h-100 flex flex-column"]',
    )

    links_de_la_pagina = []

    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    print("total of links in present page: ", len(links_de_la_pagina))

    for link in links_de_la_pagina:

        try:
            driver.get(link)

            try:
                item = driver.find_element(
                    By.XPATH,
                    '//span[@class="vtex-product-identifier-0-x-product-identifier__value"]',
                ).text
            except:
                item = ""

            try:
                title = (
                    driver.find_element(
                        By.XPATH, '//h1[contains(@class, "vtex-store-components")]/span'
                    )
                    .get_attribute("innerText")
                    .replace("\n", "")
                    .replace("\t", "")
                )
            except:
                title = ''

            try:
                price_list = driver.find_elements(
                    By.XPATH,
                    '//span[@class="vtex-store-components-3-x-currencyInteger vtex-store-components-3-x-currencyInteger--product-details"]',
                )
                if len(price_list) == 2:
                    oldprice = price_list[0].text.replace("\n", "").replace("\t", "")
                    price = price_list[1].text.replace("\n", "").replace("\t", "")
                else:
                    price = price_list[0].text.replace("\n", "").replace("\t", "")
                    oldprice = ""
            except:
                price = ""
                oldprice = ""

            try:
                categoriesxx = driver.find_elements(
                    By.XPATH, '//div[@data-testid="breadcrumb"]/span'
                )
                category_list = [
                    item.get_attribute("innerText") for item in categoriesxx
                ]
                category = category_list[2].replace("\n", "").replace("\t", "")
            except:
                category = ""

            try:
                image = driver.find_element(
                    By.XPATH, '//div[@class="vtex-store-components-3-x-productImage"]//img[@data-vtex-preload="true"]'
                ).get_attribute("src")
            except:
                image = ""

            # guardar datos
            ids.append(item)
            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            categories.append(category)
            images.append(image)

            print(
                "Item: ",
                {
                    "id": item,
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "category": category,
                    "image": image
                },
            )

            driver.back()
        except Exception as e:
            print(e)
            driver.back()

    PAGINA_INICIO += 1

dicts = {}

dicts["ids"] = ids
dicts["name"] = titles
dicts["image"] = images
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["category"] = categories

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//natue.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//natue.xlsx", ignore_index=True)
else:
    df_web.to_excel("outputs//natue.xlsx", index=False)
