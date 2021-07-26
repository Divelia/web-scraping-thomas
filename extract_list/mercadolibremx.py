from time import sleep
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
from utils import *

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()

# Definimos el User Agent en Selenium utilizando la clase Options
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

search = choose_search()

url_origin = "https://listado.mercadolibre.com.mx/{0}#D[A:{0}]".format(search)

# URL origin
driver.get(url_origin)

# get the total of results
total = driver.find_element(
    By.XPATH, '//span[@class="ui-search-search-result__quantity-results"]'
).text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = total_numbers[0]

bypage = 54

print("total of poroducts: ", total)

if total % bypage == 0:
    TOTAL_PAGES = int(total // bypage)
else:
    TOTAL_PAGES = int(total // bypage + 1)

print("Total of pages: ", TOTAL_PAGES)

titles = []
prices = []
oldprices = []
hyperlinks = []
images = []

# set pagination rules
PAGINACION_DESDE = int(input("Desde pagina: "))

# Mientras la pagina en la que me encuentre, sea menor que la maxima pagina que voy a sacar... sigo ejecutando...
m = 0


goToNext = url_origin

while True:

    while PAGINACION_DESDE > m:
        try:
            goToNext = driver.find_element_by_xpath('//a[@title="Siguiente"]').get_attribute('href')
            print('Go to ... ', goToNext)
            driver.get(goToNext)
            m += 1
        except:
            break

    sleep(random.uniform(0.0, 2.0))

    products = driver.find_elements(
        By.XPATH,
        '//section[@class="ui-search-results ui-search-results--without-disclaimer"]/ol/li',
    )

    print('Total of producst link: ', len(products))

    for index, product in enumerate(products):
        try:
            title = product.find_element_by_xpath(
                ".//h2[@class='ui-search-item__title ui-search-item__group__element']"
            ).text
        except:
            title = ""

        try:
            price = product.find_element_by_xpath(
                './/div[@class="ui-search-price__second-line"]/span[@class="price-tag ui-search-price__part"]/span[@class="price-tag-text-sr-only"]'
            ).text
        except:
            price = ""

        try:
            oldprice = product.find_element_by_xpath('.//s/span[@class="price-tag-text-sr-only"]').text
        except:
            oldprice = ""

        try:
            image = product.find_element_by_xpath('.//img[@class="ui-search-result-image__element"]').get_attribute('src')
        except Exception as e:
            print(e)
            image = ""

        try:
            hyperlink = product.find_element_by_xpath('.//a[@class="ui-search-link"]').get_attribute('href')
        except Exception as e:
            print(e)
            hyperlink = ""
    

        titles.append(title)
        prices.append(price)
        oldprices.append(oldprice)
        images.append(image)
        hyperlinks.append(hyperlink)


        # following data extracted

        print('Item: ', {
            'title': title,
            'price': price,
            'oldprice': oldprice,
            'image': image,
            'hyperlink': hyperlink
        })

    dicts = {}

    dicts["name"] = titles
    dicts["price"] = prices
    dicts["oldprice"] = oldprices
    dicts["image"] = images
    dicts["hyperlink"] = hyperlinks

    df_web = pd.DataFrame.from_dict(dicts)
    print(df_web)
    try:
        df_previous = pd.read_excel("outputs//mercadolibremx-{}.xlsx".format(search))
        print(df_previous)
    except:
        df_previous = pd.DataFrame()
        pass

    print('is empty: ', df_previous.empty)

    if df_previous.empty:
        df_web.to_excel("outputs//mercadolibremx-{}.xlsx".format(search), index=False)
    else:
        df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
        df_all_rows.to_excel("outputs//mercadolibremx-{}.xlsx".format(search), index=False)
    
    driver.back()

    PAGINACION_DESDE += 1

