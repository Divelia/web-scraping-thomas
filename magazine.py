from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
]
opts = Options()
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

url_origin = "https://magazinenatural.com.br/_loja_/_tag_/6538/suplementos"


def set_url(n):
    if n == 1:
        return url_origin
    else:
        return url_origin + "?pg={}".format(n)


print("Dont have estimation of pagination")

PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

skus = []
titles = []
images = []
prices = []

while PAGINA_FIN >= PAGINA_INICIO:

    driver.get(set_url(PAGINA_INICIO))

    print("go to ... ", set_url(PAGINA_INICIO))

    links_productos = driver.find_elements(
        By.XPATH,
        '//div[@class="loja_prod_founded"]/div/a[@class="img"]',
    )

    links_de_la_pagina = []
    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    print("Total of links in present page: ", len(links_de_la_pagina))

    for link in links_de_la_pagina:

        try:
            driver.get(link)

            try:
                title = (
                    driver.find_element(
                        By.XPATH,
                        '//td[@class="p_title"]/h1',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                title = ""

            try:
                price = (
                    driver.find_element(
                        By.XPATH,
                        '//div[@class="valor_principal valor"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                price = ""

            try:
                image = driver.find_element(
                    By.XPATH, '//div[@class="img_primary"]/img'
                ).get_attribute("src")
            except:
                image = ""

            sku = link[44:48]

            # guardar datos
            skus.append(sku)
            titles.append(title)
            prices.append(price)
            images.append(image)

            print(
                "Item: ",
                {
                    "id": sku,
                    "title": title,
                    "image": image,
                    "price": price,
                },
            )

            driver.back()
        except Exception as e:
            print(e)
            driver.back()

    PAGINA_INICIO += 1

dicts = {}

dicts["ids"] = skus
dicts["name"] = titles
dicts["image"] = images
dicts["price"] = prices

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//magazine.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//magazine.xlsx")
else:
    df_web.to_excel("outputs//magazine.xlsx", index=False)
