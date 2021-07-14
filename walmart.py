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
from utils import *

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()
opts.add_argument("user-agent=" + list_agents[2])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

search = choose_search()
search = search.capitalize()

# URL origin
url_origin = "https://www.walmart.com.mx/productos?Ntt={}".format(search)


def set_url(n):
    if n == 1:
        return url_origin
    else:
        return url_origin + "&page={}".format(n - 1)


driver.get(url_origin)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="header_title__2CdR9"]/p',
)

print(total_products_string)

total_numbers_string = [n.text for n in total_products_string]

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total_numbers_string[0])]

print("total of products  ", total_numbers[-1], " by page: ", total_numbers[0])

total_of_pages = math.ceil(total_numbers[-1]/total_numbers[0])
print("total of pages ", total_of_pages)

PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

ids = []
titles = []
brands = []
images = []
prices = []
sellbys = []
categories = []

while PAGINA_FIN >= PAGINA_INICIO:
    try:

        driver.get(set_url(PAGINA_INICIO))

        print("go to ... ", set_url(PAGINA_INICIO))

        links_productos = driver.find_elements(
            By.XPATH,
            '//div[@class="product_productCardSummary___YXeD"]/a',
        )

        links_de_la_pagina = []
        for a_link in links_productos:
            links_de_la_pagina.append(a_link.get_attribute("href"))

        print("Total of links in present page: ", len(links_de_la_pagina))

        for link in links_de_la_pagina:
            driver.get(link)
            try:
                try:
                    title = driver.find_element(
                        By.XPATH, '//h1[@data-testid="product-details-header"]'
                    ).text
                except:
                    title = ""

                try:
                    brand = (
                        driver.find_element(
                            By.XPATH, '//h2[@class="brand-name_brandName__1-04B header"]/a'
                        )
                        .get_attribute("innerText")
                    )
                except:
                    brand = ""

                try:
                    price = driver.find_element(
                        By.XPATH,
                        '//h4[@class="offer-details_minPrice__3tb1i header header_inline__ElIzA"]',
                    ).text
                except:
                    price = ""

                try:
                    sellby = driver.find_element(
                        By.XPATH, '//span[@class="product-features_blueText__pN9m6"]'
                    ).text
                except:
                    sellby = ""

                try:
                    category = driver.find_element(
                        By.XPATH,
                        '//*[@id="scrollContainer"]/section/div[1]/div[1]/ol/li[3]/a/p',
                    ).text
                except:
                    category = ""

                try:
                    image = driver.find_element(By.XPATH, '//div[@data-automation-id="hero-image"]/div/img').get_attribute("src")
                except:
                    image = ""

                try:
                    id = title[:2] + brand[:2] + price[:2] + sellby[:2] + category[:2] + image[:1]
                except:
                    id = ""


                ids.append(id)
                titles.append(title)
                brands.append(brand)
                prices.append(price)
                sellbys.append(sellby)
                categories.append(category)
                images.append(image)

                print(
                    "Item: ",
                    {
                        "id": id,
                        "title": title,
                        "brand": brand,
                        "price": price,
                        "sellby": sellby,
                        "categories": category,
                        "image": image,
                    },
                )

            except Exception as e:
                print(e)
                driver.back()

        PAGINA_INICIO += 1
    except:
        dicts = {}
        dicts["id"] = ids
        dicts["title"] = titles
        dicts["brand"] = brands
        dicts["price"] = prices
        dicts["sellby"] = sellbys
        dicts["category"] = categories
        dicts["image"] = images
        df_web = pd.DataFrame.from_dict(dicts)
        df_web.to_excel("outputs//walmart-{}.xlsx".format('backup'), index=False)

driver.close()

dicts = {}

dicts["id"] = ids
dicts["title"] = titles
dicts["brand"] = brands
dicts["price"] = prices
dicts["sellby"] = sellbys
dicts["category"] = categories
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//walmart-{}.xlsx".format(search.lower()))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//walmart-{}.xlsx".format(search.lower()), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//walmart-{}.xlsx".format(search.lower()), index=False)
