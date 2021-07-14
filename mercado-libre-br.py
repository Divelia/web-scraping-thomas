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
from time import sleep
import random

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]


opts = Options()

# Definimos el User Agent en Selenium utilizando la clase Options
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

# URL origin
driver.get("https://lista.mercadolivre.com.br/vitaminas#D[A:vitaminas]")

# get the total of results
total = driver.find_element(
    By.XPATH, '//span[@class="ui-search-search-result__quantity-results"]'
).text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = float(str(total_numbers[0]).replace('.', ''))

bypage = 56

print("total of poroducts: ", total)

if total % bypage == 0:
    TOTAL_PAGES = int(total // bypage)
else:
    TOTAL_PAGES = int(total // bypage + 1)

print("Total of pages: ", TOTAL_PAGES)


def close_modals():
    try:
        disclaimer = driver.find_element(
            By.XPATH, '//button[@id="newCookieDisclaimerButton"]'
        )
        disclaimer.click()  # lo obtenemos y le damos click
    except Exception as e:
        print(e)
        None


close_modals()

ids = []
titles = []
brands = []
prices = []
discounts = []
stocks = []
categories = []
weights = []
images = []


def set_link(n):
    if n == 1:
        link_pattern = "https://lista.mercadolivre.com.br/vitaminas#D[A:vitaminas]"
    else:
        link_pattern = (
            "https://lista.mercadolivre.com.br/saude/suplementos-alimentares/vitaminas"
            + "_Desde_"
            + str(int(51 + (n - 2) * 50))
            + "_NoIndex_True"
        )
    return link_pattern


# set pagination rules

PAGINACION_DESDE = int(input("Desde pagina: "))
if PAGINACION_DESDE < 0 | PAGINACION_DESDE > TOTAL_PAGES:
    print("pagina no debe ser menor que cero ni mayor que ", TOTAL_PAGES)
    PAGINACION_DESDE = int(input("Desde pagina: "))

PAGINACION_HASTA = int(input("Hasta pagina: "))
if PAGINACION_HASTA < 0 | PAGINACION_HASTA > TOTAL_PAGES:
    print("pagina no debe ser menor que cero ni mayor que ", TOTAL_PAGES)
    PAGINACION_HASTA = int(input("Desde pagina: "))

if len(list_agents) < PAGINACION_HASTA - PAGINACION_DESDE:
    list_agents = list_agents * (PAGINACION_HASTA - PAGINACION_DESDE)

n = 0

# Mientras la pagina en la que me encuentre, sea menor que la maxima pagina que voy a sacar... sigo ejecutando...
while PAGINACION_HASTA >= PAGINACION_DESDE:

    sleep(random.uniform(8.0, 10.0))

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

    current_link = set_link(PAGINACION_DESDE)
    print("START WITH: ", current_link)

    driver.get(current_link)

    close_modals()

    # links_products = driver.find_element_by_xpath('//section[@class="ui-search-results ui-search-results--without-disclaimer"]//ol/li//a[@class="ui-search-result__content ui-search-link"]')

    time.sleep(2)

    links_products = driver.find_elements(
        By.XPATH,
        '//ol[@class="ui-search-layout ui-search-layout--stack"]/li//a[@class="ui-search-item__group__element ui-search-link"]',
    )

    # print(links_products)

    links_de_la_pagina = []

    for a_link in links_products:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    for link in links_de_la_pagina:

        try:
            # Voy a cada uno de los links de los detalles de los productos
            driver.get(link)

            title = (
                driver.find_element(By.XPATH, '//h1[@class="ui-pdp-title"]')
                .text.replace("\n", "")
                .replace("\t", "")
            )
            price = (
                driver.find_element(
                    By.XPATH,
                    '//div[@class="ui-pdp-price__second-line"]/span/span/span[@class="price-tag-fraction"]',
                )
                .text.replace("\n", "")
                .replace("\t", "")
            )
            try:
                find_discount = (
                    driver.find_element(
                        By.XPATH,
                        '//s/span[@class="price-tag-text-sr-only"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except: 
                find_discount = ""

            print('oldprice: ', find_discount)

            try:

                if "Antes" in find_discount:
                    nums = [float(s) for s in re.findall(r"-?\d+\.?\d*", find_discount)]
                    discount = nums[0]
                else:
                    discount = ""
            except:
                pass

            stock = (
                driver.find_element(
                    By.XPATH, '//span[@class="ui-pdp-buybox__quantity__selected"]'
                )
                .text.replace("\n", "")
                .replace("\t", "")
            )
            category_list = driver.find_elements(
                By.XPATH, '//a[@class="andes-breadcrumb__link"]'
            )
            category = category_list[-1].text.replace("\n", "").replace("\t", "")
            print("category: ", category)

            table = driver.find_elements_by_xpath(
                './/tbody[@class="andes-table__body"]/tr'
            )
            print(len(table))

            if table:
                for tr in driver.find_elements(
                        By.XPATH,
                    './/tbody[@class="andes-table__body"]/tr'
                ):
                    ths = tr.find_elements_by_tag_name("th")
                    headers_name = [th.text for th in ths]
                    values_name = tr.find_elements_by_tag_name("td")
                    values = [td.text for td in values_name]
                    try:
                        if "Marca" == headers_name[0].replace("\n", "").replace("\t", ""):
                            brand = values[0]
                    except:
                        brand = ""
                    try:
                        if "Peso líquido" == headers_name[0].replace("\n", "").replace("\t", ""):
                            weight = values[0]
                    except:
                        weight = ""

            image_list = driver.find_elements(By.XPATH, '//figure[@class="ui-pdp-gallery__figure"]/img')
            image = image_list[0].get_attribute("src")

            ids.append(link[41:50])
            titles.append(title)
            brands.append(brand)
            prices.append(price)
            discounts.append(discount)
            stocks.append(stock)
            categories.append(category)
            weights.append(weight)
            images.append(image)

            print('Item: ', {
                'id': link[41:50],
                'title': title,
                'brand': brand,
                'price': price,
                'discount': discount,
                'stock': stock,
                'category': category,
                'weight': weight,
                'image': image
            })
            # Aplasto el boton de retroceso
            driver.back()
        except Exception as e:
            print(e)
            # Si sucede algun error dentro del detalle, no me complico. Regreso a la lista y sigo con otro producto.
            driver.back()

    PAGINACION_DESDE += 1
    n += 1


driver.close()

dicts = {}

dicts["id"] = ids
dicts["name"] = titles
dicts["brand"] = brands
dicts["price"] = prices
dicts["oldprice"] = discounts
dicts["stock"] = stocks
dicts["category"] = categories
dicts["weight"] = weights
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//mercado-libre-br.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
#   df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows.to_excel("outputs//mercado-libre-br.xlsx", index=False)    
else:
  df_web.to_excel("outputs//mercado-libre-br.xlsx", index=False)
