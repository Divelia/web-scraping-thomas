from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tqdm import tqdm

from utils import *

search = choose_search()

if search == 'suplementos':
    n = 20
else:
    n = 50

url_origin = 'https://www.benavides.com.mx/?q={0}&size=n_{1}_n'.format(search, n)

# Definimos el User Agent en Selenium utilizando la clase Options
opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")
opts.add_argument("--start-maximized")
# opts.add_argument("--disable-extensions")
# current_ip = generate_ip()
# opts.add_argument('--proxy-server={}'.format(current_ip))
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

print('Going to... ', url_origin)
driver.get(url_origin)

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
    driver.quit()
    
    opts = Options()
    current_agent = generate_agents()
    opts.add_argument("user-agent=" + current_agent)
    current_ip = generate_ip()
    opts.add_argument('--proxy-server={}'.format(current_ip))
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

driver.close()

dicts['id'] = skus
dicts['name'] = names
dicts['quantity'] = quantities
dicts['image'] = images

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//benavides-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//benavides-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//benavides-{}.xlsx".format(search), index=False)

print('File generated ... , benavides-{}.xlsx'.format(search))