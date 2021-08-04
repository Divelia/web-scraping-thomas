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

url_origin = "https://listado.mercadolibre.com.mx/{0}#D[A:{0}]".format(search)

# URL origin
driver.get(url_origin)

# get the total of results
total = driver.find_element(
    By.XPATH, '//span[@class="ui-search-search-result__quantity-results"]'
).text

total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

total = total_numbers[0]

bypage = 54

print("total of poroducts: ", total)

if total % bypage == 0:
    TOTAL_PAGES = int(total // bypage)
else:
    TOTAL_PAGES = int(total // bypage + 1)

print("Total of pages: ", TOTAL_PAGES)

hyperlinks = []
titles = []
brands = []
prices = []
discounts = []
stocks = []
categories = []
weights = []
images = []
kits = []

# set pagination rules
PAGINACION_DESDE = int(input("Desde pagina: "))

# Mientras la pagina en la que me encuentre, sea menor que la maxima pagina que voy a sacar... sigo ejecutando...


goToNext = url_origin

m = 0

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
        links_productos = driver.find_elements(By.XPATH, '//section[@class="ui-search-results ui-search-results--without-disclaimer"]/ol//a[@class="ui-search-link"]')
    except Exception as e:
        print(e)
        links_productos = []

    links_de_la_pagina = []

    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))
        
    sleep(random.uniform(0.0, 2.0))

    print('Total of producst link: ', len(links_de_la_pagina))

    try:
        for index, link_product in enumerate(links_de_la_pagina):

            print(link_product)

            try:
                # Voy a cada uno de los links de los detalles de los productos
                print('Going to ... ', link_product)
                driver.get(link_product)

                try:
                    title = (
                        driver.find_element(By.XPATH, '//h1[@class="ui-pdp-title"]')
                        .text.replace("\n", "")
                        .replace("\t", "")
                    )
                except:
                    title = ''

                try:
                    price = (
                        driver.find_element(
                            By.XPATH,
                            '//div[@class="ui-pdp-price__second-line"]/span/span/span[@class="price-tag-fraction"]',
                        )
                        .text.replace("\n", "")
                        .replace("\t", "")
                    )
                except:
                    price = ''

                try:
                    find_discount = (
                        driver.find_element(
                            By.XPATH,
                            '//s/span[@class="price-tag-text-sr-only"]',
                        )
                        .text.replace("\n", "")
                        .replace("\t", "")
                    )
                    # print(find_discount)
                except:
                    find_discount = ""

                try:

                    if "Antes" in find_discount:
                        nums = [float(s) for s in re.findall(r"-?\d+\.?\d*", find_discount)]
                        discount = nums[0]
                    else:
                        discount = ""
                except:
                    pass
                # print('disccount: ', discount)
                stock = (
                    driver.find_element(
                        By.XPATH, '//span[@class="ui-pdp-buybox__quantity__selected"]'
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
                category_list = driver.find_elements(
                    By.XPATH, '//a[@class="andes-breadcrumb__link"]'
                )
                category = category_list[-1].text.replace("\n", "").replace("\t", "")
                # print("category: ", category)

                image_list = driver.find_elements(By.XPATH, '//figure[@class="ui-pdp-gallery__figure"]/img')
                image = image_list[0].get_attribute("src")

                table = driver.find_elements_by_xpath(
                    './/tbody[@class="andes-table__body"]/tr'
                )
                # print(len(table))

                # search in table for extra information as marca and peso neto
                if table:

                    headers = [tr.find_element_by_tag_name("th") for tr in table]
                    headers_name = [th.text for th in headers]

                    values = [tr.find_element_by_tag_name("td") for tr in table]
                    values_name = [td.text for td in values]

                    # print('headers: ', headers_name)
                    # print('marca is in ? ')
                    if 'Marca' in headers_name:
                        indexof = headers_name.index('Marca')
                        brand = values_name[indexof]
                    else:
                        brand = ''

                    if 'Peso neto' in headers_name:
                        indexof = headers_name.index('Peso neto')
                        weight = values_name[indexof]
                    else:
                        weight = ''

                    if 'Unidades por pack' in headers_name:
                        indexof = headers_name.index('Unidades por pack')
                        kit = values_name[indexof]
                    else:
                        kit = ''

                # print("brand: ", brand)
                # print("weight: ", weight)

                titles.append(title)
                brands.append(brand)
                prices.append(price)
                discounts.append(discount)
                stocks.append(stock)
                categories.append(category)
                weights.append(weight)
                kits.append(kit)
                images.append(image)
                hyperlinks.append(link_product)

                # following data extracted

                print('Item: ', {
                    'title': title,
                    'brand': brand,
                    'price': price,
                    'oldprice': discount,
                    'stock': stock,
                    'category': category,
                    'weight': weight,
                    'kit': kit,
                    'image': image,
                    'hyperlink': link_product
                })

                driver.back()
            except Exception as e:
                # break
                continue
                # print(e)
                # driver.quit()
                # opts = Options()
                # opts.add_argument("--start-maximized")
                # # current_agent = generate_agents()
                # # opts.add_argument("user-agent=" + current_agent)
                # # current_ip = generate_free_proxy()
                # # opts.add_argument('--proxy-server={}'.format(current_ip))
                # driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
                # m = 0


        PAGINACION_DESDE += 1
    except:
        opts = Options()
        opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")
        opts.add_argument("--start-maximized")

        # Definimos el User Agent en Selenium utilizando la clase Options
        opts.add_argument("user-agent=" + random.choice(list_agents))

        driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

    dicts = {}

    dicts["name"] = titles
    dicts["brand"] = brands
    dicts["price"] = prices
    dicts["oldprice"] = discounts
    dicts["stock"] = stocks
    dicts["category"] = categories
    dicts["weight"] = weights
    dicts["kit"] = kits
    dicts["image"] = images
    dicts["hyperlink"] = hyperlinks

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
    
    # driver.back()


