from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
]
opts = Options()
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

def set_url(n):
    url_origin = 'https://www.farmaciasanpablo.com.mx/vitaminas-y-suplementos/c/09?q=%3Arelevance&page={}'.format(n)
    return url_origin


PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

ids = []
titles = []
# brands = []
prices = []
oldprices = []
quantities = []
categories = []
images = []

while PAGINA_FIN >= PAGINA_INICIO:

  driver.get(set_url(PAGINA_INICIO-1))

  links_productos = driver.find_elements(By.XPATH, '//div[@class="row items  product-listing product-list"]//div[contains(@class, "img-wrap")]/a')
  links_de_la_pagina = []

  for a_link in links_productos:
    links_de_la_pagina.append(a_link.get_attribute("href"))

  print('total of links in present page: ', len(links_de_la_pagina))

  for link in links_de_la_pagina:

    try:
      driver.get(link)

      item = driver.find_element(By.XPATH, '//div[@class="single-product-details"]/div[2]/dl/dd[2]').text
      idlist = [float(s) for s in re.findall(r'-?\d+\.?\d*', item)]
      item = idlist[0]

      try:
        title = driver.find_element(By.XPATH, '//div[@class="single-product-details"]/div[@class="col-md-6 col-xs-12"]//h1[@class="item-title"]').get_attribute('innerText').replace("\n", "").replace("\t", "")
      except:
        title = driver.find_element_by_xpath('//div[@class="single-product-details"]/div[@class="col-md-6 col-xs-12"]//h1[@class="item-title"]').text.replace("\n", "").replace("\t", "")

      price = driver.find_elements(By.XPATH, '//div[@class="row product-detail"]//p[@class="item-prize narrow"]')[0].text.replace("\n", "").replace("\t", "")

      try:
        oldprice = driver.find_elements(By.XPATH, '//div[@class="row product-detail"]//p[@class="item-prize narrow"]/del')[0].text.replace("\n", "").replace("\t", "")
      except:
        oldprice = ''

      try:
        quantity = driver.find_element(By.XPATH, '//div[@class="single-product-details"]/div[2]/dl/dd[1]').text
      except:
        quantity = ''

      try:
        categoriesxx = driver.find_elements(By.XPATH, '//ol[@class="breadcrumb"]/li/a')
        category_list = [item.get_attribute('innerText') for item in categoriesxx]
        category = category_list[-2].replace("\n", "").replace("\t", "")
      except:
        category = ''

      image = driver.find_element(By.XPATH, '//div[@class="owl-item active center"]/img').get_attribute("src")

      # guardar datos
      ids.append(item)
      titles.append(title)
      prices.append(price)
      oldprices.append(oldprice)
      quantities.append(quantity)
      images.append(image)
      categories.append(category)

      print('Item: ', {
        'id': item,
        'title': title,
        # 'brand': title,
        'price': price,
        'oldprice': oldprice,
        'quantity': quantity,
        'image': image,
        'category': category
      })


      driver.back()
    except Exception as e:
      print (e)
      driver.back()

  PAGINA_INICIO += 1

driver.close()
dicts = {}

dicts["id"] = ids
dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["quantity"] = quantities
dicts["image"] = images
dicts["category"] = categories


df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//san_pablo_farmacia.xlsx")
except:
    df_previous = None
    pass

print(df_previous)

if df_previous is not None:
  df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows.to_excel("outputs//san_pablo_farmacia.xlsx", index=False)
else:
  df_web.to_excel("outputs//san_pablo_farmacia.xlsx", index=False)