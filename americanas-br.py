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
]
opts = Options()
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)


def set_url(n):
    if n == 1:
        link_pattern = "https://www.americanas.com.br/busca/suplementos"
    else:
        link_pattern = (
            "https://www.americanas.com.br/busca/suplementos"
            + "?limit=24&offset="
            + str(int(24 * (n - 1)))
        )
    return link_pattern


PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

titles = []
prices = []
oldprices = []
categories = []
images = []

while PAGINA_FIN >= PAGINA_INICIO:
    time.sleep(random.uniform(1.0, 10.0))
    driver.get(set_url(PAGINA_INICIO))
    print("starts with ", set_url(PAGINA_INICIO))

    links_productos = driver.find_elements(
        By.XPATH,
        '//div[@class="grid__StyledGrid-sc-1man2hx-0 iFeuoP"]/div//a[@aria-current="page"]',
    )
    print("len of products ", len(links_productos))

    links_de_la_pagina = []

    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    print("total of links in present page: ", len(links_de_la_pagina))

    for link in links_de_la_pagina:
        print('presnet linkt: ', link)
        try:
            driver.get(link)

            try:
                title = driver.find_element(By.XPATH, '//span[@class="src__Text-sc-154pg0p-0 product-title__Title-sc-1hlrxcw-0 hoBeMD"]').text.replace("\n", "").replace("\t", "")
            except:
                title = ""

            try:
                price_list = (
                    driver.find_elements(
                        By.XPATH,
                        '//div[@class="src__BestPrice-sc-1jvw02c-5 cBWOIB priceSales"]',
                    )
                )
                price = price_list[-1].text.replace("\n", "").replace("\t", "")
            except:
                price = ""

            try:
                oldprice = (
                    driver.find_elements(
                        By.XPATH, '//span[@class="src__ListPrice-sc-1jvw02c-2 kXsrBq"]'
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                oldprice = ""

            try:
                categories = driver.find_elements(
                    By.XPATH, '//ul[@class="src__List-sc-11934zu-1 fQHwSt"]/li/a'
                )
                category_list = [item.get_attribute("innerText") for item in categories]
                category = category_list[-1].replace("\n", "").replace("\t", "")
            except:
                category = ""

            try:
                image_list = driver.find_elements(
                    By.XPATH,
                    '//picture[@class="src__Picture-xr9q25-2 fYTOXR"]/img[@loading="lazy"]',
                )
                image = image_list[0].get_attribute("src")
            except:
                image = ""

            # guardar datos
            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            categories.append(category)
            images.append(image)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "category": category,
                    "image": image,
                },
            )

            driver.back()
        except Exception as e:
            print(e)
            driver.back()

    PAGINA_INICIO += 1

driver.close()
dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["category"] = categories
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//americanas-br.xlsx")
except:
    df_previous = None
    pass

print(df_previous)

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//americanas-br.xlsx", index=False)
else:
    df_web.to_excel("outputs//americanas-br.xlsx", index=False)
