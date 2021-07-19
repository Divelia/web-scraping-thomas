
from time import sleep
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
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
opts.add_argument("--disable-notifications")

search = choose_search()

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

# URL origin
url_origin = "https://www.walmart.com.mx/productos?Ntt={}".format(search.capitalize())

def set_link(n):
    if n == 1:
        return url_origin
    else:
        return url_origin + "&page={}".format(n-1)

driver.get(url_origin)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//p[@class="text_text__3oq-D text_secondary__2NFr8 text_inline__3fF4P text_small__z1_6W"]'))
)

total_products_string = driver.find_elements(
    By.XPATH,
    '//p[@class="text_text__3oq-D text_secondary__2NFr8 text_inline__3fF4P text_small__z1_6W"]',
)
total_products = int(get_list_of_numbers(total_products_string[-1].text)[-1])

total_products_bypage = driver.find_elements(
    By.XPATH,
    '//div[contains(@data-automation-id, "production-index")]',
)
bypage = len(total_products_bypage)

print('total of products  ', total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of clicks: ", total_of_pages)


titles = []
prices = []
oldprices = []
images = []
brands = []
promos = []

tries = 0

PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

while PAGINA_FIN >= PAGINA_INICIO:
    try:
        driver.get(set_link(PAGINA_INICIO))

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="flex_noMargin__2nisT flex_noPadding__1fg2H row"]/div'))
        )

        list_of_products = driver.find_elements(By.XPATH, '//div[@class="flex_noMargin__2nisT flex_noPadding__1fg2H row"]/div')

        sleep(random.uniform(1.0, 3.0))

        for product in list_of_products:


            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, './/img[@class="image_image__3RXgV"]'))
            )

            try:
                try:
                    title = product.find_element_by_xpath('.//div[@class="ellipsis"]').text
                except:
                    title = ''
                try:
                    price = product.find_element_by_xpath('.//p[@class="text_text__3oq-D text_large__K4EIS text_bold__2Ptj-"]').text
                except:
                    price = ''
                try:
                    oldprice = product.find_element_by_xpath('.//span[@class="product_strike__9Pjv1"]').text
                except:
                    oldprice = ''
                try:
                    image = product.find_element_by_xpath('.//img[@class="image_image__3RXgV"]').get_attribute("src")
                except:
                    image = ''
                try:
                    brand = product.find_element_by_xpath('.//div[contains(@class, "product_brand")]').text
                except:
                    brand = ''
                try:
                    promo = product.find_element_by_xpath(
                        './/p[@class="text_text__3oq-D text_small__z1_6W"]').text
                except:
                    promo = ''

                titles.append(title)
                prices.append(price)
                oldprices.append(oldprice)
                images.append(image)
                brands.append(brand)
                promos.append(promo)

                print(
                    "Item: ",
                    {
                        "title": title,
                        "price": price,
                        "oldprice": oldprice,
                        "image": image,
                        "brand": brand,
                        "promo": promo
                    },
                )

            except Exception as e:
                print(e)
    except Exception as e:
        if tries < 5:
            tries += 1
            continue
        else:
            print(driver.current_url)
            break

    PAGINA_INICIO += 1

driver.close()

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images
dicts["brand"] = brands
dicts["promo"] = promos

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//walmart-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//walmart-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//walmart-{}.xlsx".format(search), index=False)

