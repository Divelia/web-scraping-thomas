import re
import random
import pandas as pd
from time import sleep
from utils import *
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()
opts.add_argument("user-agent=" + list_agents[2])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-notifications")

driver = webdriver.Chrome("./chromedriver", chrome_options=opts)

search = choose_search()

if search == 'suplementos':
    n = 20
else:
    n = 50

url_origin = 'https://www.benavides.com.mx/?q={0}&size=n_{1}_n'.format(search, n)


print("Going to... ", url_origin)

driver.get(url_origin)

sleep(random.uniform(5, 7))


PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

n = 0

titles = []
prices = []
images = []

error = False

while PAGINACION_HASTA >= PAGINACION_DESDE:

    print("Start page number {}".format(PAGINACION_DESDE))

    # randomize requests
    sleep(random.uniform(5, 7))

    try:
        current_url = url_origin
        print("Going to... ", current_url)

        products = driver.find_elements(
            By.XPATH,
            '//section[contains(@class, "search__ResultsWrap-wz1dy5-2")]/div',
        )

        for index, product in enumerate(products):
            try:
                title = product.find_element_by_xpath(
                    ".//a[@class='title-result']"
                ).get_attribute('innerText')
            except:
                title = ""
            try:
                price = product.find_element_by_xpath('.//div[@class="pricing"]/span[last()]').get_attribute('textContent')
            except:
                price = ""

            try:
                image = product.find_element_by_xpath(
                    './/picture/img'
                ).get_attribute('src')
            except Exception as e:
                print(e)
                image = ""

            titles.append(title)
            prices.append(price)
            images.append(image)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
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
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//benavides-{}.xlsx".format(search))
except:
    df_previous = pd.DataFrame()
    pass

if df_previous.empty:
    df_web.to_excel("outputs//benavides-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//benavides-{}.xlsx".format(search), index=False)
