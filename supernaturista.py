from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import math
from utils import *
import random

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
]

search = choose_search()
search = search[:-1]

opts = Options()
opts.add_argument("user-agent=" + list_agents[0])
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

def set_url(n):
    url_origin = 'https://supernaturista.com/search?page={0}&q={1}%2A&type=article%2Cpage%2Cproduct'.format(n, search)
    return url_origin

print('Going to... ', set_url(1))

driver.get(set_url(1))

total_products_string = driver.find_element(By.XPATH, '//nav[@class="breadcrumbs-container"]/span[2]').text
total_products = [float(s) for s in re.findall(r"-?\d+\.?\d*", total_products_string)][0]

bypage = 24

print('Total of pages: ', math.ceil(total_products/bypage))

PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

skus = []
titles = []
images = []
brands = []
prices = []
oldprices = []

while PAGINA_FIN >= PAGINA_INICIO:

  driver.get(set_url(PAGINA_INICIO))

  links_productos = driver.find_elements(By.XPATH, '//ul[@class="productgrid--items products-per-row-3"]/li/div[@class="productitem"]/a')
  links_de_la_pagina = []

  for a_link in links_productos:
    links_de_la_pagina.append(a_link.get_attribute("href"))

  print('total of links in present page: ', len(links_de_la_pagina))

  for link in links_de_la_pagina:
    print(link)

    try:
      driver.get(link)

      sku_string = driver.find_element(By.XPATH, '//div[@class="product-description rte"]/b').text
      sku = [s for s in re.findall(r"-?\d+\.?\d*", total_products_string)][0]
      title = driver.find_element(By.XPATH, '//div[@class="product-main"]//div[@class="product-details"]/h1').text
      brand = driver.find_element(By.XPATH, '//div[@class="product-vendor"]/a').text
      image = driver.find_element(By.XPATH, '//div[@class="product-gallery--image-background"]/img').get_attribute("src")
      price = driver.find_element(By.XPATH, '//div[@class="product--price "]/div[@class="price--main"]/span[@class="money"]').text
      try:
        oldprice = driver.find_element(By.XPATH, '//div[@class="product--price "]/div[@class="price--compare-at visible"]/span[@class="money"]').text
      except:
        oldprice = ''

      print(
          "Item: ",
          {
              "id": sku,
              "name": title,
              "oldprice": oldprice,
              "price": price,
              "brand": brand,
              "image": image,
          },
      )

      # guardar datos
      skus.append(sku)
      titles.append(title)
      brands.append(brand)
      images.append(image)
      prices.append(price)
      oldprices.append(oldprice)
      
      driver.back()
    except Exception as e:
      driver.quit()
      opts = Options()
      current_agent = generate_agents()
      opts.add_argument("user-agent={}".format(current_agent))
      current_ip = generate_ip()
      opts.add_argument('--proxy-server={}'.format(current_ip))
      driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

  PAGINA_INICIO += 1
dicts = {}

dicts["ids"] = skus
dicts["name"] = titles
dicts["brand"] = brands
dicts["image"] = images
dicts["oldprice"] = oldprices
dicts["price"] = prices

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//supernaturista-{}.xlsx".format(search))
except:
    df_previous = None
    pass

if df_previous is not None:
  df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows.to_excel("outputs//supernaturista-{}.xlsx".format(search))
else:
  df_web.to_excel("outputs//supernaturista-{}.xlsx".format(search), index=False)