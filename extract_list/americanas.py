
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
url_origin = "https://www.americanas.com.br/busca/{}".format(search)

driver.get(url_origin)

total_products_string = driver.find_elements(
    By.XPATH,
    '//span[@class="full-grid__TotalText-sc-19t7jwc-2 dtGPLs"]',
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
stocks = []
promos = []

tries = 0

while True:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="src__Container-sc-82ugau-0 fkBfxf"]//ul/li[last()]//button[@class="src__PageButton-sc-82ugau-3 fhogRv"]'))
        )

        list_of_products = driver.find_elements(By.XPATH, '//div[contains(@class, "grid__StyledGrid-sc-1man2hx-0 iFeuoP")]/div')

        for product in list_of_products:
            try:
                try:
                    title = product.find_element_by_xpath('.//span[@class="src__Text-sc-154pg0p-0 src__Name-sc-1k0ejj6-2 kcJuNs"]').text
                except:
                    title = ''
                try:
                    price = product.find_element_by_xpath('.//span[@class="src__Text-sc-154pg0p-0 src__PromotionalPrice-sc-1k0ejj6-6 cbiYUL"]').text
                except:
                    price = ''
                try:
                    oldprice = product.find_element_by_xpath('.//span[@class="src__Text-sc-154pg0p-0 src__Price-sc-1k0ejj6-5 gSjAEC"]').text
                except:
                    oldprice = ''
                try:
                    image = product.find_element_by_xpath('.//picture[@class="src__Picture-xr9q25-2 fYTOXR"]/img').get_attribute("src")
                except:
                    image = ''
                try:
                    promo = product.find_element_by_xpath('.//span[@class="src__PaymentDetails-sc-1k0ejj6-3 src__Installment-sc-1k0ejj6-4 hLXDbj"]').text
                except:
                    promo = ''
                try:
                    stock = product.find_element_by_xpath(
                        './/span[@class="src__Count-r5o9d7-1 izzoCr"]').text
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
                EC.presence_of_element_located((By.XPATH, '//div[@class="src__Container-sc-82ugau-0 fkBfxf"]//ul/li[last()]//button[@class="src__PageButton-sc-82ugau-3 fhogRv"]'))
            )

            button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="src__Container-sc-82ugau-0 fkBfxf"]//ul/li[last()]//button[@class="src__PageButton-sc-82ugau-3 fhogRv"]'))
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
    df_previous = pd.read_excel("outputs//americanas-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//americanas-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//americanas-{}.xlsx".format(search), index=False)
