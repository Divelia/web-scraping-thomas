from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import time
import random
from utils import *
import math
# from amazoncaptcha import AmazonCaptcha

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()

opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")
opts.add_argument("--start-maximized")

# Definimos el User Agent en Selenium utilizando la clase Options
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

search = choose_search()

url_origin = "https://www.amazon.com.mx/s?k={}".format(search)

# URL origin
driver.get(url_origin)

# get the total of results
total = driver.find_element(
    By.XPATH, '//div[@class="sg-col-14-of-20 sg-col s-breadcrumb sg-col-10-of-16 sg-col-6-of-12"]//span[1]'
).text

print('total: ', total)

total_of_products = get_list_of_numbers(total.replace(",", ""))[-1]

print(total_of_products)

bypage = get_list_of_numbers(total.replace(",", ""))[-2]

print("total of products: ", total_of_products)

TOTAL_PAGES = math.ceil(total_of_products / bypage)

print("Total of pages: ", TOTAL_PAGES)

titles = []
prices = []
oldprices = []
brands = []
contents = []
images = []
hyperlinks = []

# set pagination rules
PAGINACION_DESDE = int(input("Desde pagina: "))

# Mientras la pagina en la que me encuentre, sea menor que la maxima pagina que voy a sacar... sigo ejecutando...
m = 0

goToNext = url_origin

while True:

    while PAGINACION_DESDE > m:
        try:
            goToNext = driver.find_element_by_xpath('//a[@title="Siguiente"]').get_attribute('href')
            print('Go to ... ', goToNext)
            driver.get(goToNext)
            m += 1
        except:
            break

    try:
        links_productos = driver.find_elements(By.XPATH, '//a[@class="a-link-normal s-no-outline"]')
    except Exception as e:
        print(e)
        links_productos = []

    links_de_la_pagina = []

    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))
        
    sleep(random.uniform(0.0, 2.0))

    print('Total of producst link: ', len(links_de_la_pagina))

    for index, link_product in enumerate(links_de_la_pagina):

        print(link_product)

        try:
            # Voy a cada uno de los links de los detalles de los productos
            print('Going to ... ', link_product)
            driver.get(link_product)

            try:
                title = (
                    driver.find_element(By.XPATH, '//span[@id="productTitle"]')
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                title = ''

            if title == '':
                sleep(10)
                # captcha = AmazonCaptcha.from_webdriver(driver)
                # solution = captcha.solve()

            try:
                price = (
                    driver.find_element(
                        By.XPATH,
                        '//span[@id="price_inside_buybox"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                price = ''

            try:
                oldprice = (
                    driver.find_element(
                        By.XPATH,
                        '//span[@class="priceBlockStrikePriceString a-text-strike"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                oldprice = ''

            try:
                brand = (
                    driver.find_element(
                        By.XPATH,
                        '//a[@id="bylineInfo"]',
                    )
                    .text.replace("Marca: ", "").replace("\n", "")
                    .replace("\t", "")
                )
            except:
                price = ''

            try:
                content = (
                    driver.find_element(
                        By.XPATH,
                        '//table[@class="a-normal a-spacing-micro"]//tr[last()]//span[@class="a-size-base"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                content = ''

            try:
                image = (
                    driver.find_element(
                        By.XPATH,
                        '//ul[@class="a-unordered-list a-nostyle a-horizontal list maintain-height"]/li[last()]//img[@data-a-manual-replacement="true"]',
                    )
                    .get_attribute('src')
                )
            except:
                image = ''

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            brands.append(brand)
            contents.append(content)
            images.append(image)
            hyperlinks.append(link_product)

            # following data extracted

            print('Item: ', {
                'title': title,
                'price': price,
                'oldprice': oldprice,
                'brand': brand,
                'content': content,
                'image': image,
                'hyperlink': link_product
            })

            driver.back()
        except Exception as e:
            print(e)
            driver.quit()
            opts = Options()
            opts.add_argument("--start-maximized")
            current_agent = generate_agents()
            opts.add_argument("user-agent=" + current_agent)
            current_ip = generate_free_proxy()
            opts.add_argument('--proxy-server={}'.format(current_ip))
            driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
            m = 0


    PAGINACION_DESDE += 1

    dicts = {}

    dicts["name"] = titles
    dicts["brand"] = brands
    dicts["price"] = prices
    dicts["oldprice"] = oldprices
    dicts["content"] = contents
    dicts["image"] = images
    dicts["hyperlink"] = hyperlinks

    df_web = pd.DataFrame.from_dict(dicts)
    print(df_web)
    try:
        df_previous = pd.read_excel("outputs//amazonmx-{}.xlsx".format(search))
        print(df_previous)
    except:
        df_previous = pd.DataFrame()
        pass

    print('is empty: ', df_previous.empty)

    if df_previous.empty:
        df_web.to_excel("outputs//amazonmx-{}.xlsx".format(search), index=False)
    else:
        df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
        df_all_rows.to_excel("outputs//amazonmx-{}.xlsx".format(search), index=False)
    
    # driver.back()


