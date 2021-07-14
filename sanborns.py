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
    url_origin = "https://www.sanborns.com.mx/resultados/q=Vitaminas/{}".format(n)
    return url_origin

driver.get(set_url(1))

# get the total of results
total = driver.find_element(
    By.XPATH, '//div[@id="resultadoBusqueda"]'
).text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]
total = total_numbers[0]
bypage = 48

print("total of products: ", total)
if total % bypage == 0:
    TOTAL_PAGES = int(total // bypage)
else:
    TOTAL_PAGES = int(total // bypage + 1)
print("Total of pages: ", TOTAL_PAGES)


PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))


skus = []
titles = []
images = []
descriptions = []
prices = []
oldprices = []

while PAGINA_FIN >= PAGINA_INICIO:

    time.sleep(random.uniform(1.0, 5.0))

    driver.get(set_url(PAGINA_INICIO))

    links_productos = driver.find_elements(
        By.XPATH, '//div[@class="rowProductos"]/article/a[1]'
    )

    prices_products_xpath = driver.find_elements(
        By.XPATH, '//span[contains(@class, "preciodesc money")]'
    )
    prices_products = [price.text for price in prices_products_xpath]

    oldprices_products_xpath = driver.find_elements(
        By.XPATH, '//div[@class="infoDesc"]'
    )

    oldprices_products = []
    for d in oldprices_products_xpath:
      try:
        oldprices_products.append(
            d.find_element(By.XPATH, '//span[contains(@class, "precioant money")]').text
        )
      except:
        oldprices_products.append('')

    links_de_la_pagina = []

    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    print("total of links in present page: ", len(links_de_la_pagina))

    n = 0
    for link in links_de_la_pagina:

        try:
            driver.get(link)
            try:
                sku = driver.find_element(
                    By.XPATH, '//div[@class="box_Entrega"]/div[1]/p'
                ).text
            except:
                sku = ""
            try:
                title = driver.find_element(
                    By.XPATH, '//section[@class="productMainTitle"]/div/h1'
                ).text
            except:
                title = ""
            try:
                price = prices_products[n]
            except:
                price = ""
            try:
                oldprice = oldprices_products[n]
            except:
                oldprice = ""
            try:
                image = driver.find_element(
                    By.XPATH, '//ul[@class="carrusel-producto oneImage"]/li/img'
                ).get_attribute("src")
            except:
                image = ""
            try:
                description = driver.find_element(
                    By.XPATH, '//p[@id="verCompleto"]'
                ).text
            except:
                description = ""

            n += 1
            # guardar datos
            skus.append(sku)
            titles.append(title)
            images.append(image)
            prices.append(price)
            oldprices.append(oldprice)
            descriptions.append(description)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "sku": skus,
                    "description": description,
                    "image": image,
                },
            )

            driver.back()
        except Exception as e:
            print(e)
            driver.back()

    PAGINA_INICIO += 1

dicts = {}

dicts["id"] = skus
dicts["name"] = titles
dicts["image"] = images
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["description"] = descriptions

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//sanborns.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//sanborns.xlsx")
else:
    df_web.to_excel("outputs//sanborns.xlsx", index=False)
