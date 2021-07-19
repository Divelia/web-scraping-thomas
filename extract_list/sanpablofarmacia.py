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
def set_link(n):
  if n == 1:
    return "https://www.farmaciasanpablo.com.mx/vitaminas-y-suplementos/c/09"
  else:
    return 'https://www.farmaciasanpablo.com.mx/vitaminas-y-suplementos/c/09?q=%3Arelevance&page={}'.format(n-1)

driver.get(set_link(1))

total_products_string = driver.find_elements(
    By.XPATH,
    '//span[@class="counter"]',
)

xx = [n.text for n in total_products_string][0]

total_products = get_list_of_numbers(xx)

total_products_bypage = driver.find_elements(
    By.XPATH,
    '//div[@class="row items  product-listing product-list"]/div',
)
bypage = len(total_products_bypage)

print("Total of products: ", total_products[-1])
print("Total of pages: ", math.ceil(total_products[-1]/bypage))

titles = []
prices = []
quantities = []
images = []

tries = 0

PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

while PAGINACION_HASTA >= PAGINACION_DESDE:
    try:
        print('Go to ', set_link(PAGINACION_DESDE))

        driver.get(set_link(PAGINACION_DESDE))

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="row items  product-listing product-list"]/div'))
        )

        list_of_products = driver.find_elements(By.XPATH, '//div[@class="row items  product-listing product-list"]/div')

        for product in list_of_products:
            try:
                try:
                    title = product.find_element_by_xpath('.//p[@class="item-title"]').text
                except:
                    title = ''

                try:
                    price = product.find_element_by_xpath('.//p[@class="item-prize"]').text
                except:
                    price = ''

                try:
                    quantity = product.find_element_by_xpath('.//p[@class="item-subtitle"]').text
                except:
                    quantity = ''

                try:
                    image = product.find_element_by_xpath('.//img[@class="item-image img-responsive lazy"]').get_attribute("src")
                except:
                    image = ''

                titles.append(title)
                quantities.append(quantity)
                prices.append(price)
                images.append(image)

                print(
                    "Item: ",
                    {
                        "title": title,
                        "quantity": quantity,
                        "price": price,
                        "image": image,
                    },
                )

            except Exception as e:
                print(e)

        PAGINACION_DESDE += 1

    except Exception as e:
        if tries < 5:
            tries += 1
            continue
        else:
            print(driver.current_url)
            break

driver.close()

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["image"] = images
dicts["quantity"] = quantities

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//sanpablofarmacia-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//sanpablofarmacia-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//sanpablofarmacia-{}.xlsx".format(search), index=False)

