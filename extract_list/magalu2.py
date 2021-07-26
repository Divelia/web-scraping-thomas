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

# URL origin
search = choose_search()

url_origin = "https://www.magazineluiza.com.br/busca/{}/".format(search)

current_agent = generate_agents()

opts = Options()
opts.add_argument("user-agent=" + current_agent)
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")
current_agent = generate_agents()
opts.add_argument("user-agent={}".format(current_agent))
current_ip = generate_free_proxy()
opts.add_argument("--proxy-server={}".format(current_ip))

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)


print("Going to... ", url_origin)


def set_link(n):
    if n == 1:
        link_pattern = 'https://www.magazineluiza.com.br/busca/suplemento%20A2F%20Laboratorio%20Farmacêutico/'
    else:
        link_pattern = url_origin + str(int(n))
    return link_pattern

driver.get(set_link(1))

# get the total of results
total = driver.find_element(By.XPATH, '//h1[@itemprop="description"]/small').text
total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]
total = total_numbers[0]

bypage = 60

print("Total of poroducts: ", total)

TOTAL_PAGES = math.ceil(total / bypage)

print("Total of pages: ", TOTAL_PAGES)

titles = []
prices = []
oldprices = []
images = []
kits = []
hyperlinks = []

# set pagination rules
# PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
# PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

urlnext = set_link(1)

n = 0

# Mientras la pagina en la que me encuentre, sea menor que la maxima pagina que voy a sacar... sigo ejecutando...
while True:

    n += 1
    # current_link = set_link(PAGINACION_DESDE)
    # print("Going to ...", current_link)

    if n > TOTAL_PAGES:
      break

    try:
        driver.get(urlnext)
    except:
        break

    # links_products = driver.find_element_by_xpath('//section[@class="ui-search-results ui-search-results--without-disclaimer"]//ol/li//a[@class="ui-search-result__content ui-search-link"]')

    sleep(random.uniform(1.0, 5.0))

    links_products = driver.find_elements(
        By.XPATH,
        '//ul[@class="productShowCase big"]/li[contains(@id, "product_")]',
    )

    products = driver.find_elements_by_xpath(
        '//ul[@class="productShowCase big"]/li[contains(@id, "product_")]'
    )

    try:

        for index, product in enumerate(products):
            try:
                title = product.find_element_by_xpath(
                    ".//h3[@class='productTitle']"
                ).text
            except:
                title = ""

            try:
                oldprice = product.find_element_by_xpath(
                    './/span[@class="productPrice"]/span[@class="originalPrice"]'
                ).text
            except:
                oldprice = ""

            try:
                kit = product.find_element_by_xpath(
                    './/span[@class="installmentPrice"]'
                ).text
            except:
                kit = ""

            try:
                price = (
                    (product.find_element_by_xpath('.//span[@class="price-value"]'))
                    .text.replace("\n", " ")
                    .replace("\r", " ")
                    .strip()
                )
            except:
                try:
                    price = (
                        (product.find_element_by_xpath('.//span[@class="price"]'))
                        .text.replace("\n", " ")
                        .replace("\r", " ")
                        .strip()
                    )
                except:
                    price = ""
            try:
                image = product.find_element_by_xpath(
                    './/img[@class="product-image"]'
                ).get_attribute("src")
            except Exception as e:
                print(e)
                image = ""

            try:
                hyperlink = product.find_element_by_xpath(
                    './/a[@itemprop="url"]'
                ).get_attribute("href")
            except Exception as e:
                print(e)
                hyperlink = ""

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            images.append(image)
            kits.append(kit)
            hyperlinks.append(hyperlink)

            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "image": image,
                    "kit": kit,
                    "hyperlinks": hyperlink
                },
            )

        dicts = {}

        dicts["name"] = titles
        dicts["price"] = prices
        dicts["oldprice"] = oldprices
        dicts["image"] = images
        dicts["promo"] = kits
        dicts["hyperlink"] = hyperlinks

        df_web = pd.DataFrame.from_dict(dicts)
        print(df_web)
        try:
            df_previous = pd.read_excel("outputs//magalu-{}.xlsx".format(search))
            print(df_previous)
        except:
            df_previous = pd.DataFrame()
            pass

        print("is empty: ", df_previous.empty)

        if df_previous.empty:
            df_web.to_excel("outputs//magalu-{}.xlsx".format(search), index=False)
        else:
            df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
            df_all_rows.to_excel("outputs//magalu-{}.xlsx".format(search), index=False)

            try:
                goToNext = product.find_element_by_xpath(
                    '//div[@class="center"]/a[last()-1]'
                ).get_attribute("href")
                urlnext = goToNext
                print('urlnext: ', urlnext)
            except:
                continue

    except Exception as e:
        driver.quit()
        current_agent = generate_agents()
        opts.add_argument("user-agent={}".format(current_agent))
        current_ip = generate_free_proxy()
        opts.add_argument("--proxy-server={}".format(current_ip))
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)


