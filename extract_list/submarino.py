
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
url_origin = "https://www.submarino.com.br/busca/{0}?content={1}&filter=%7B%22id%22%3A%22categoria%22%2C%22value%22%3A%22Suplementos+e+{2}%22%2C%22fixed%22%3Afalse%7D&sortBy=relevance&source=nanook&testab=searchTestAB%3Dold&rc={1}".format(search, search.upper(), search.capitalize())

driver.get(url_origin)

total_products_string = driver.find_elements(
    By.XPATH,
    '//span[@class="full-grid__TotalText-fvrmdp-2 BPXil"]',
)
xx = [n.text for n in total_products_string][0].replace(' ', '').replace('.', '')

total_products = get_list_of_numbers(xx)

total_products_bypage = driver.find_elements(
    By.XPATH,
    '//div[contains(@class, "grid__StyledGrid-sc-1man2hx-0 iFeuoP")]/div',
)
bypage = len(total_products_bypage)

print('total of products  ', total_products[0], ' by page: ', bypage)

total_of_pages = math.ceil(total_products[0] / bypage)
print("total of clicks: ", total_of_pages)


titles = []
prices = []
oldprices = []
images = []
promos = []
stocks = []

tries = 0

while True:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "grid__StyledGrid-sc-1man2hx-0 iFeuoP")]/div//span[@class="src__Text-sc-154pg0p-0 src__Name-r60f4z-1 keKVYT"]'))
        )

        list_of_products = driver.find_elements(By.XPATH, '//div[contains(@class, "grid__StyledGrid-sc-1man2hx-0 iFeuoP")]/div')

        for product in list_of_products:
            try:
                try:
                    title = product.find_element_by_xpath('.//span[@class="src__Text-sc-154pg0p-0 src__Name-r60f4z-1 keKVYT"]').text
                except:
                    title = ''
                try:
                    price = product.find_element_by_xpath('.//span[@class="src__Text-sc-154pg0p-0 src__PromotionalPrice-r60f4z-6 kTMqhz"]').text
                except:
                    price = ''
                try:
                    oldprice = product.find_element_by_xpath('.//span[@class="src__Text-sc-154pg0p-0 src__Price-r60f4z-5 izVeKJ"]').text
                except:
                    oldprice = ''
                try:
                    image = product.find_element_by_xpath('.//picture[@class="src__Picture-xr9q25-2 fYTOXR"]/img').get_attribute("src")
                except:
                    image = ''
                try:
                    promo = product.find_element_by_xpath('.//span[@class="src__PaymentDetails-r60f4z-2 src__Installment-r60f4z-3 dGPFSs"]').text
                except:
                    promo = ''
                try:
                    stock = product.find_element_by_xpath(
                        './/span[@class="src__Count-mqnvif-1 dXgUhg"]').text
                except:
                    stock = ''

                titles.append(title)
                prices.append(price)
                oldprices.append(oldprice)
                images.append(image)
                promos.append(promo)
                stocks.append(stock)

                print(
                    "Item: ",
                    {
                        "title": title,
                        "price": price,
                        "oldprice": oldprice,
                        "image": image,
                        "promo": promo,
                        "stock": stock
                    },
                )

            except Exception as e:
                print(e)
        try:
            sleep(random.uniform(1.0, 5.0))

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//ul[@class="src__Items-sc-3s0b0c-1 bJyqHy"]/li[9]//button[@class="src__PageButton-sc-3s0b0c-2 emvgpX"]'))
            )

            button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//ul[@class="src__Items-sc-3s0b0c-1 bJyqHy"]/li[9]//button[@class="src__PageButton-sc-3s0b0c-2 emvgpX"]'))
            )

            driver.execute_script("arguments[0].click();", button)
        except:
            break
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
dicts["oldprice"] = oldprices
dicts["image"] = images
dicts["promo"] = promos
dicts["stock"] = stocks

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//submarino-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//submarino-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//submarino-{}.xlsx".format(search), index=False)

