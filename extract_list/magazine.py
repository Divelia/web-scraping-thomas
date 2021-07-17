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
if search == 'vitaminas':
    url_origin = "https://magazinenatural.com.br/_loja_/_busca_/{}".format(search)
else:
    url_origin = "https://magazinenatural.com.br/_loja_/_tag_/6538/{}".format(search)

driver.get(url_origin)

titles = []
prices = []
images = []

tries = 0

while True:
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="loja_prod_founded"]/div'))
        )

        list_of_products = driver.find_elements(By.XPATH, '//div[@class="loja_prod_founded"]/div')

        for product in list_of_products:
            try:
                try:
                    title = product.find_element_by_xpath('.//div[@class="nome"]/a').text
                except:
                    title = ''
                try:
                    price = product.find_element_by_xpath('.//div[@class="valor"]').text
                except:
                    price = ''
                try:
                    image = product.find_element_by_xpath('.//a[@class="img"]').get_attribute("outerHTML")
                except:
                    image = ''

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

            except Exception as e:
                print(e)
        try:
            sleep(random.uniform(1.0, 5.0))
            nextpage = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@title="Próxima Página"]'))
            ).get_attribute('href')

            driver.get(nextpage)
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
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//magazine-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//magazine-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//magazine-{}.xlsx".format(search), index=False)

