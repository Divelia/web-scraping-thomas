from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tqdm import tqdm

# Definimos el User Agent en Selenium utilizando la clase Options
opts = Options()
# opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)
driver.get('https://www.benavides.com.mx/?q=vitamina&size=n_50_n')

try:
  disclaimer = driver.find_element(By.XPATH, '//a[@aria-label="Entendido"]')
  disclaimer.click() # lo obtenemos y le damos click
except Exception as e:
  print (e)
  None

links_productos = driver.find_elements(By.XPATH, '//section[starts-with(@class, "search__Result")]//a')

links_de_la_pagina = []

for a_link in links_productos:
  links_de_la_pagina.append(a_link.get_attribute("href"))

dicts = {}
names = []
prices = []
skus = []
quantities = []
images = []

for link in tqdm(links_de_la_pagina):
  try: 
    driver.get(link)

    product_name = WebDriverWait(driver, 10).until(
       EC.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "Productcontent")]/h2'))
    ).text
    # print(product_name)
    
    sku = WebDriverWait(driver, 10).until(
       EC.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "Productcontent")]//span[@itemprop="sku"]'))
    ).text
    # print(sku)

    price = WebDriverWait(driver, 10).until(
       EC.presence_of_element_located((By.XPATH, '//span[@itemprop="price"]'))
    ).text
    print(price)

    quantity = driver.find_elements(By.XPATH, '//div[starts-with(@class, "Productcontent")]//div[starts-with(@class, "slug__Size")]/span')

    details = []
    for d in quantity:
      details.append(d.text.replace('\n', ' ').replace('\r', ' ').strip())

    image = driver.find_element(By.XPATH, '//div[@class="Productcontent text-center"]//picture/img').get_attribute("src")
    # print('image: ', image)

    names.append(product_name.replace('\n', ' ').replace('\r', ' ').strip())
    skus.append(sku.replace('\n', ' ').replace('\r', ' ').strip())
    prices.append(price.replace('\n', ' ').replace('\r', ' ').strip())
    quantities.append(' '.join(details))
    images.append(image)


  except Exception as e:
    print (e)
    driver.back()


dicts['sku'] = skus
dicts['name'] = names
dicts['quantities'] = quantities
dicts['image'] = images

df_web = pd.DataFrame.from_dict(dicts)

print(df_web)

df_web.to_excel('benavides.xlsx') 
