from time import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
from bs4 import BeautifulSoup
from time import sleep
import random
from utils import *
import math
import requests
from lxml import html
 
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
}
search = choose_search()

opts = Options()

opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

url_origin = "https://listado.mercadolibre.com.mx/{0}#D[A:{0}]".format(search)


print('Going to... ', url_origin)

driver.get(url_origin)

total = driver.find_element(
    By.XPATH, '//span[@class="ui-search-search-result__quantity-results"]'
).text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = float(str(total_numbers[0]).replace('.', ''))

bypage = 56

print("total of poroducts: ", total)

TOTAL_PAGES = math.ceil(total // bypage)

print("Total of pages: ", TOTAL_PAGES)

driver.close()

ids = []
titles = []
brands = []
prices = []
discounts = []
stocks = []
categories = []
weights = []
images = []
unidades_por_kit = []


def set_link(n):
    if n == 1:
        link_pattern = "https://listado.mercadolibre.com.mx/{}".format(search)
    else:
        link_pattern = (
            "https://listado.mercadolibre.com.mx/{}".format(search)
            + "_Desde_"
            + str(int(49 + (n - 2) * 48))
        )
    return link_pattern



PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

n = 0

titles = []
brands = []
prices = []
oldprices = []
images = []



while PAGINACION_HASTA >= PAGINACION_DESDE:

    print('Start page number {}'.format(PAGINACION_DESDE))
    sleep(random.uniform(1.0, 5.0))

    try:
        current_url = set_link(PAGINACION_DESDE)
        print('Going to... ', current_url)
        driver.get(current_url)

        products = driver.find_elements_by_xpath("//ol[@class='ui-search-layout ui-search-layout--stack']/li")

        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        
        for product in products:
            try:
                # title = product.xpath(".//h2[@class='ui-search-item__title']/text()")[0]
                title = product.find_element_by_xpath(".//h2[@class='ui-search-item__title']").text
            except:
                title = ''
            try:
                # price = product.xpath('.//div[@class="ui-search-price__second-line"]/span[@class="price-tag ui-search-price__part"]/span[@class="price-tag-text-sr-only"]/text()')[0].replace(' reais con', '.').replace(' centavos', '').replace(' ', '')
                prices = product.find_elements_by_xpath('.//div[@class="ui-search-price__second-line"]/span[@class="price-tag ui-search-price__part"]/span[@class="price-tag-text-sr-only"]')
                price = [p.text for p in prices][0]
            except:
                price = ''
            try:
                # oldprice = product.xpath('.//s/span[@class="price-tag-text-sr-only"]/text()')[0].replace('Antes: ', '').replace(' reais', '')
                oldprice = product.find_element_by_xpath('.//s/span[@class="price-tag-text-sr-only"]').text.replace('Antes: ', '').replace(' reais', '')
            except:
                oldprice = ''
            try:
                WebDriverWait(product, 20).until(EC.presence_of_element_located((By.XPATH, "//img[@class='ui-search-result-image__element']")))
                image = [n.get_attribute("currentSrc") for n in product.find_elements(By.XPATH, ".//img[@class='ui-search-result-image__element']")][0]
            except:
                
                image = ''

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprices)
            images.append(image)

            print('Item: ', {
                'title': title,
                'price': price,
                'oldprice': oldprice,
                'image': image,
            })


        PAGINACION_DESDE += 1
        print('Finish page number {}'.format(PAGINACION_DESDE))
        n += 1
        if PAGINACION_DESDE > PAGINACION_HASTA:
            print('Scraper finished')
            break

        print('PAGINACION_DESDE: ', PAGINACION_DESDE, ' ', int(PAGINACION_DESDE))
        print('PAGINACION_HASTA: ', PAGINACION_HASTA, ' ', int(PAGINACION_HASTA))
    except Exception as e:
        print(e)
        print('cant access to link')
        print('changing proxy')
        driver.quit()
        opts = Options()
        current_agent = generate_agents()
        opts.add_argument("user-agent=" + current_agent)
        current_ip = generate_ip()
        opts.add_argument('--proxy-server={}'.format(current_ip))
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)
        # url_web = requests.get(current_url, proxies={'http': proxy, 'https': proxy}, timeout=3)
        continue

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