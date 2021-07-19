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
opts.add_argument("user-agent=" + list_agents[1])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-notifications")

search = choose_search()

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

# URL origin
url_origin = "https://www.lojadosuplemento.com.br/pesquisa?t={}".format(search.upper())

def set_link(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = url_origin + "#/pagina-{}".format(n)
    return link_pattern

driver.get(url_origin)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="wrapper text"]//p/strong'))
)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="wrapper text"]//p/strong',
)

print(total_products_string)

total_products = int(get_list_of_numbers(total_products_string[-1].text)[-1])

total_products_bypage = driver.find_elements(
    By.XPATH,
    '//div[@class="wd-browsing-grid-list   wd-widget-js"]/ul/li',
)

bypage = len(total_products_bypage)

print('total of products  ', total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of clicks: ", total_of_pages)


titles = []
prices = []
oldprices = []
images = []
unique_prices = []
lmpm_prices = []

tries = 0

PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

while PAGINA_FIN >= PAGINA_INICIO:
    try:
        print('Going to ', set_link(PAGINA_INICIO))
        driver.get(set_link(PAGINA_INICIO))

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='wd-browsing-grid-list   wd-widget-js']/ul/li//div[@class='block-1 savings']/strong"))
        )

        list_of_products = driver.find_elements(By.XPATH, "//div[@class='wd-browsing-grid-list   wd-widget-js']/ul/li")

        sleep(random.uniform(1.0, 3.0))

        for product in list_of_products:


            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="wd-browsing-grid-list   wd-widget-js"]/ul/li//div[@class="block-1 savings"]/strong'))
            )

            try:
                try:
                    title = product.find_element_by_xpath(".//div[@class='name']/a").text
                except:
                    title = ''

                try:
                    price = product.find_element_by_xpath('.//div[@class="block-1 savings"]/strong').text
                except:
                    price = ''

                try:
                    oldprice = product.find_element_by_xpath('.//div[@class="block-1 savings"]/del').text
                except:
                    oldprice = ''

                try:
                    image = product.find_element_by_xpath('.//div[@class="variation variation-root"]/img').get_attribute("src")
                except:
                    image = ''

                try:
                    unique_price = product.find_element_by_xpath(
                        './/div[@class="block-2 condition"]/span[1]'
                    ).text.replace('\n', ' ').replace('\r', ' ').strip()
                except:
                    unique_price = ''

                try:
                    lmpm_pricex = product.find_elements_by_xpath(".//div[@class='block-2 condition']/span")
                    lmpm_pricexx = [n.text.replace('\n', ' ').replace('\r', ' ').strip() for n in lmpm_pricex]
                    lmpm_price = lmpm_pricexx[1] + lmpm_pricexx[2]
                except:
                    lmpm_price = ''

                titles.append(title)
                prices.append(price)
                oldprices.append(oldprice)
                images.append(image)
                unique_prices.append(unique_price)
                lmpm_prices.append(lmpm_price)

                print(
                    "Item: ",
                    {
                        "title": title,
                        "price": price,
                        "oldprice": oldprice,
                        "image": image,
                        "unique_price": unique_price,
                        "lmpm_price": lmpm_price
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
dicts["unique_price"] = unique_prices
dicts["lmpm_price"] = lmpm_prices

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//lojadosuplemento-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//lojadosuplemento-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//lojadosuplemento-{}.xlsx".format(search), index=False)

