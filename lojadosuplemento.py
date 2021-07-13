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

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

def set_url(n):
    if n == 1:
        url_origin = 'https://www.lojadosuplemento.com.br/pesquisa?t=VITAMINAS'
    else:
        url_origin = 'https://www.lojadosuplemento.com.br/pesquisa?t=VITAMINAS#/pagina-{}'.format(n)
    return url_origin

driver.get(set_url(1))

total_products_string = driver.find_element(
    By.XPATH,
    '//div[@class="search-description"]//p/strong',
).text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total_products_string.replace(",", ""))]

bypage = 15
total_products = total_numbers[0]

print('total of products  ',total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of pages ", total_of_pages)

PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

titles = []
brands = []
prices = []
oldprices = []
quantities = []
descriptions = []
images = []

while PAGINA_FIN >= PAGINA_INICIO:

  driver.get(set_url(PAGINA_INICIO))

  links_productos = driver.find_elements(By.XPATH, '//article/div[contains(@class,"wd-browsing-grid-list")]/ul/li//a[@class="thumb"]')
  links_de_la_pagina = []

  for a_link in links_productos:
    links_de_la_pagina.append(a_link.get_attribute("href"))

  print('total of links in present page: ', len(links_de_la_pagina))

  for link in links_de_la_pagina:

    try:
      driver.get(link)

      try:
        title = driver.find_element(By.XPATH, '//div[@class="block-3"]/h1').text.replace('\n', '').replace('\t', '')
      except:
        title = ''
      try:
        oldprice_list = driver.find_elements(By.XPATH, '//div[@class="block-1 savings"]/del')
        oldprice = oldprice_list[0].text.replace('\n', '').replace('\t', '')
      except:
        oldprice = ''
      try:
        price_list = driver.find_elements(By.XPATH, '//div[@class="block-1 savings"]/strong[@class="best-price"]')
        price = price_list[0].get_attribute('innerText').replace('\n', '').replace('\t', '')
      except:
        price = ''
      try:
        brand = driver.find_element(By.XPATH, '//a[@class="brand"]').text.replace('\n', '').replace('\t', '')
      except:
        brand = ''
      try:
        quantity = driver.find_element(By.XPATH, '//div[@class="presentation"]/p').text.replace('\n', '').replace('\t', '')
      except:
        quantity = ''
      try:
        description = driver.find_element(By.XPATH, '//div[@id="LongDescription"]/div[@class="text"]').text.replace('\n', '').replace('\t', '')
      except:
        description = ''
      try:
        image = driver.find_element(By.XPATH, '//img[@class="image Image"]').get_attribute("src")
      except:
        image = ''

      print(
          "Item: ",
          {
              "title": title,
              "price": price,
              "oldprice": oldprice,
              "brand": brand,
              "quantity": quantity,
              "description":  description,
              "image": image,
          },
      )

      # guardar datos
      titles.append(title)
      prices.append(price)
      oldprices.append(oldprice)
      brands.append(brand)
      quantities.append(quantity)
      descriptions.append(description)
      images.append(image)

      driver.back()
    except Exception as e:
      print (e)
      continue

  PAGINA_INICIO += 1

driver.close()

dicts = {}

dicts["name"] = titles
dicts["brand"] = brands
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["quantity"] = quantities
dicts["description"] = descriptions
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//lojadosuplemento.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
  df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows.to_excel("outputs//lojadosuplemento.xlsx")
else:
  df_web.to_excel("outputs//lojadosuplemento.xlsx", index=False)