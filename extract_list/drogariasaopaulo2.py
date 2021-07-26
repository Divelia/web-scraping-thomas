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
url_origin = "https://www.drogariasaopaulo.com.br/pesquisa?q={}".format(search)

driver.get(url_origin)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="info-pagination"]/span/b',
)

bypage = int(total_products_string[0].text.replace(' ', ''))
total_products = int(total_products_string[1].text.replace(' ', ''))

print('total of products  ',total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of clicks: ", total_of_pages)

# for page in tqdm(range(1)):
for page in tqdm(range(1, total_of_pages)):
    try:
        sleep(random.uniform(1.0, 2.0))

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="text-center btn-load-more"]/button'))
        )

        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="text-center btn-load-more"]/button'))
        )

        driver.execute_script("arguments[0].click();", button)

        # button.click()

    except Exception as e:
        print(e)
        pass

list_of_products = driver.find_elements(By.XPATH, '//div[@class="prateleira vitrine default chaordic-search-list n12colunas"]/ul/li')

titles = []
prices = []
oldprices = []
images = []
hyperlinks = []

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@class="prateleira vitrine default chaordic-search-list n12colunas"]/ul/li//a[@class="collection-image-link"]/img'))
    )

    list_of_products = driver.find_elements(By.XPATH, '//div[@class="prateleira vitrine default chaordic-search-list n12colunas"]/ul/li')

    for product in list_of_products:
        try:
            try:
                title = product.find_element_by_xpath('.//a[@class="collection-link"]').text
            except:
                title = ''

            try:
                price = product.find_element_by_xpath('.//div[@class="valor"]/span').text
            except:
                price = ''

            try:
                oldprice = product.find_element_by_xpath('.//div[@class="valor-de"]/span').text
            except:
                oldprice = ''

            try:
                image = product.find_element_by_xpath('.//a[@class="collection-image-link"]/img').get_attribute("src")
            except:
                image = ''

            try:
                hyperlink = product.find_element_by_xpath('.//a[@class="collection-image-link"]').get_attribute("href")
            except:
                hyperlink = ''

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            images.append(image)
            hyperlinks.append(hyperlink)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "image": image,
                    "oldprice": oldprice,
                    "hyperlink": hyperlink
                },
            )

        except Exception as e:
            print(e)

except Exception as e:
    print(e)

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images
dicts["hyperlink"] = hyperlinks

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//drogariasaopaulo-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//drogariasaopaulo-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//drogariasaopaulo-{}.xlsx".format(search), index=False)

