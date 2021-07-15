from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import math
import re

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
]
opts = Options()
opts.add_argument("user-agent=" + list_agents[0])
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

url_origin = 'https://www.sams.com.mx/search/Ntt=Vitaminas'

driver.get(url_origin)

total_products_string = driver.find_element(
    By.XPATH,
    '//div[@class="left counter "]',
).text

print(total_products_string)

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total_products_string.replace(",", ""))]

print('total of products  ',total_numbers)

# PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
# PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

items = []
titles = []
brands = []
prices = []
oldprices = []
quantities = []
descriptions = []
images = []

links_productos = driver.find_elements(By.XPATH, '//div[@class="product-listing  desktop"]//a[@class="item-image"]')
links_de_la_pagina = []

for a_link in links_productos:
  links_de_la_pagina.append(a_link.get_attribute("href"))

print('total of links in present page: ', len(links_de_la_pagina))

for link in links_de_la_pagina:

  try:
    driver.get(link)

    try:
        item = driver.find_element(By.XPATH, '//span[@class="prod-id"]')
    except:
        item = ''
    try:
      title = driver.find_element(By.XPATH, '//h1[@class="prod-name"]').text.replace('\n', '').replace('\t', '')
    except:
      title = ''
    try:
      oldprice = driver.find_element(By.XPATH, '//span[@class="price-before-value"]')
    except:
      oldprice = ''
    try:
      price = driver.find_element(By.XPATH, 'prod-price-actual').text.replace('\n', '').replace('\t', '')
    except:
      price = ''
    try:
      brand = driver.find_element(By.XPATH, '//a[@class="prod-brand"]').text.replace('\n', '').replace('\t', '')
    except:
      brand = ''
    try:
      image = driver.find_element(By.XPATH, '//img[@class="lazy-image zoom-image lazyloaded"]').get_attribute("src")
    except:
      image = ''

    print(
        "Item: ",
        {
            "item": item,
            "title": title,
            "price": price,
            "oldprice": oldprice,
            "brand": brand,
            "image": image,
        },
    )

    # guardar datos
    items.append(item)
    titles.append(title)
    prices.append(price)
    oldprices.append(oldprice)
    brands.append(brand)
    images.append(image)

    driver.back()
  except Exception as e:
    print (e)
    continue

  PAGINA_INICIO += 1

driver.close()

dicts = {}

dicts["id"] = items
dicts["name"] = titles
dicts["brand"] = brands
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//sams.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
  df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows.to_excel("outputs//sams.xlsx")
else:
  df_web.to_excel("outputs//sams.xlsx", index=False)