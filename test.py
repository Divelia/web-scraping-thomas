from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from utils import *
import random
from time import sleep

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
]

search = choose_search()
search = search[:-1]

url_origin = "https://www.drogaraia.com.br/bem-estar/{}.html".format(search)

print("Going to... ", url_origin)

opts = Options()
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

def set_url(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = url_origin + "?p={}".format(n)
    return link_pattern


PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

titles = []
brands = []
prices = []
oldprices = []
unique_prices = []
lmpm_prices = []
images = []

while PAGINA_FIN >= PAGINA_INICIO:

  sleep(random.uniform(1.0, 3.0))

  driver.get(set_url(PAGINA_INICIO))

  products = driver.find_elements(By.XPATH, '//div[@class="col-main-before"]//p[@class="amount inline amount--has-pages"]')

  for product in products:
    try:
      try:
          title = product.find_element_by_xpath('.//a[@class="show-hover"]').text
      except:
          title = ""
      try:
          oldprice = product.find_element_by_xpath(
              './/p[@class="old-price"]/span[@class="price"]'
          ).text
      except:
          oldprice = ""

      try:
          unique_price = product.find_element_by_xpath(
              './/div[@class="price unique-price"]//span[@class="lmpm-price-text"]'
          ).text
          lmpm_price = (
              product.find_element_by_xpath('.//div[@class="price lmpm-price"]').text
              + product.find_element_by_xpath(
                  './/div[@class="price lmpm-price"]//span[@class="accent lmpm-price-text"]'
              ).text
          )
      except:
          unique_price = ""
          lmpm_price = ""

      try:
          price = product.find_element_by_xpath(
              './/p[@class="special-price"]/span[@class="price"]'
          ).text
      except:
          try:
              price = product.find_element_by_xpath(
                  './/span[@class="regular-price"]/span'
              ).text
          except:
              price = ""
      try:
          image = product.xpath(
              './/img[contains(@id, "product-collection-image-")]'
          ).get_attribute('src')
      except Exception as e:
          print(e)
          image = ""

      titles.append(title)
      prices.append(price)
      oldprices.append(oldprice)
      unique_prices.append(unique_price)
      lmpm_prices.append(lmpm_price)
      images.append(image)

      print(
          "Item: ",
          {
              "title": title,
              "price": price,
              "oldprice": oldprice,
              "unique_price": unique_price,
              "lmpm_price": lmpm_price,
              "image": image,
          },
      )

    except Exception as e:
      print (e)
      driver.back()

  PAGINA_INICIO += 1

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["unique_price"] = unique_prices
dicts["lmpm_price"] = lmpm_prices
dicts["oldprice"] = oldprices
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)

print(df_web)

try:
    df_previous = pd.read_excel("outputs//drogaria-{}.xlsx".format(search))
except:
    df_previous = None
    pass

if df_previous is not None:
  df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
  df_all_rows.to_excel("outputs//drogaria-{}.xlsx".format(search), index=False)
else:
  df_web.to_excel("outputs//drogaria-{}.xlsx".format(search), index=False)