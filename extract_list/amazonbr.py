# # from time import time
# import re
# import random
# import requests
# import pandas as pd
# from time import sleep
# from bs4 import BeautifulSoup
# from lxml import html
# from utils import *
# import math

# headers = {
#     "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
# }

# search = choose_search()

# url_origin = "https://www.amazon.com.br/s?k={}".format(search)

# print("Going to... ", url_origin)

# response = requests.get(url_origin, headers=headers)

# parser = html.fromstring(response.text)

# # soup = BeautifulSoup(response.text)

# total = parser.xpath(
#     '//div[@class="a-section a-spacing-small a-spacing-top-small"]/span[1]/text()'
# )[0].replace(".", "")

# total_of_products = get_list_of_numbers(total)[-1]
# bypage = -get_list_of_numbers(total)[-2]

# print("total of poroducts: ", total_of_products)

# TOTAL_PAGES = math.ceil(total_of_products / bypage)

# print("Total of pages: ", TOTAL_PAGES)


# def set_link(n):
#     if n == 1:
#         link_pattern = url_origin
#     else:
#         link_pattern = "https://www.amazon.com.br/s?k={}".format(
#             search
#         ) + "&page={}/".format(n)
#     return link_pattern


# PAGINACION_DESDE = int(input("Extraer datos desde pagina: "))
# PAGINACION_HASTA = int(input("Extraer datos hasta pagina: "))

# n = 0

# titles = []
# prices = []
# oldprices = []
# images = []

# error = False

# while PAGINACION_HASTA >= PAGINACION_DESDE:

#     print("Start page number {}".format(PAGINACION_DESDE))

#     # randomize requests
#     sleep(random.uniform(1.0, 3.0))

#     try:
#         current_url = set_link(PAGINACION_DESDE)
#         print("Going to... ", current_url)

#         # requests parser
#         if error:
#             current_proxy = generate_free_proxy()
#             responsexxx = requests.get(
#                 current_url,
#                 headers=headers,
#                 proxies={
#                     # "http": "http://" + str(current_proxy),
#                     "https": "https://" + str(current_proxy),
#                     # "ftp": "ftp://" + str(current_proxy),
#                 },
#             )
#         else:
#             responsexxx = requests.get(current_url, headers=headers)


#         parser = html.fromstring(responsexxx.text)
#         products = parser.xpath("//div[@data-component-type='s-search-result']")
#         # beautiful soup parser
#         # soup = BeautifulSoup(response.text)
#         # products_soup = soup.find_all('div', class_="ui-search-layout__item")

#         for index, product in enumerate(products):
#             try:
#                 title = product.xpath(
#                     ".//span[@class='a-size-base-plus a-color-base a-text-normal']/text()"
#                 )[0]
#             except:
#                 title = ""
#             try:
#                 price = (
#                     product.xpath(
#                         './/span[@data-a-size="l"]//span[@class="a-price-whole"]/text()'
#                     )[0]
#                     + "."
#                     + product.xpath(
#                         './/span[@data-a-size="l"]//span[@class="a-price-fraction"]/text()'
#                     )[0]
#                 )
#             except:
#                 price = ""
#             try:
#                 oldprice = product.xpath(
#                     './/span[@class="a-price a-text-price"]/span[@class="a-offscreen"]/text()'
#                 )[0]
#             except:
#                 oldprice = ""
#             try:
#                 image = product.xpath(
#                     './/div[@class="a-section aok-relative s-image-square-aspect"]/img[@class="s-image"]/@src'
#                 )[0]
#             except Exception as e:
#                 print(e)
#                 image = ""

#             titles.append(title)
#             prices.append(price)
#             oldprices.append(oldprice)
#             images.append(image)

#             print(
#                 "Item: ",
#                 {
#                     "title": title,
#                     "price": price,
#                     "oldprice": oldprice,
#                     "image": image,
#                 },
#             )

#         PAGINACION_DESDE += 1
#         print("Finish page number {}".format(PAGINACION_DESDE))
#         n += 1
#         if PAGINACION_DESDE > PAGINACION_HASTA:
#             print("Scraper finished")
#             break

#         print("PAGINACION_DESDE: ", PAGINACION_DESDE, " ", int(PAGINACION_DESDE))
#         print("PAGINACION_HASTA: ", PAGINACION_HASTA, " ", int(PAGINACION_HASTA))

#     except Exception as e:
#         print(e)
#         error = True
#         print("cant access to link")

#         continue

# dicts = {}

# dicts["name"] = titles
# dicts["price"] = prices
# dicts["oldprice"] = oldprices
# dicts["image"] = images

# df_web = pd.DataFrame.from_dict(dicts)
# print(df_web)

# try:
#     df_previous = pd.read_excel("outputs//amazonbr-{}.xlsx".format(search))
# except:
#     df_previous = pd.DataFrame()
#     pass

# if df_previous.empty:
#     df_web.to_excel("outputs//amazonbr-{}.xlsx".format(search), index=False)
# else:
#     df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
#     df_all_rows.to_excel("outputs//amazonbr-{}.xlsx".format(search), index=False)


# from scrapy.item import Field
# from scrapy.item import Item
# from scrapy.spiders import CrawlSpider, Rule
# from scrapy.selector import Selector
# from scrapy.linkextractors import LinkExtractor
# from scrapy.loader.processors import MapCompose
# from scrapy.loader import ItemLoader
# from utils import *

# search = choose_search()

# # URL origin
# url_origin = "https://www.lojadosuplemento.com.br/pesquisa?t={}".format(search.upper())


# class Product(Item):
#     name = Field()
#     price = Field()
#     oldprice = Field()
#     image = Field()

# class Lojadosuplemento(CrawlSpider):
#     name = 'lojadosuplemento'
#     custom_settings = {
#         "DOWNLOADER_MIDDLEWARES": { # pip install Scrapy-UserAgents
#             'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#             'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
#         },
#         "USER_AGENTS": [
#             ('Mozilla/5.0 (X11; Linux x86_64) '
#              'AppleWebKit/537.36 (KHTML, like Gecko) '
#              'Chrome/57.0.2987.110 '
#              'Safari/537.36'),  # chrome
#             ('Mozilla/5.0 (X11; Linux x86_64) '
#              'AppleWebKit/537.36 (KHTML, like Gecko) '
#              'Chrome/61.0.3163.79 '
#              'Safari/537.36'),  # chrome
#             ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
#              'Gecko/20100101 '
#              'Firefox/55.0'),  # firefox
#             ('Mozilla/5.0 (X11; Linux x86_64) '
#              'AppleWebKit/537.36 (KHTML, like Gecko) '
#              'Chrome/61.0.3163.91 '
#              'Safari/537.36'),  # chrome
#             ('Mozilla/5.0 (X11; Linux x86_64) '
#              'AppleWebKit/537.36 (KHTML, like Gecko) '
#              'Chrome/62.0.3202.89 '
#              'Safari/537.36'),  # chrome
#             ('Mozilla/5.0 (X11; Linux x86_64) '
#              'AppleWebKit/537.36 (KHTML, like Gecko) '
#              'Chrome/63.0.3239.108 '
#              'Safari/537.36'),  # chrome
#             # Sigues anadiendo cuantos user agents quieras rotar...
#         ]    }

#     allowed_domains = ['www.lojadosuplemento.com.br']
#     start_urls = [url_origin]
#     download_delay = 1

#     rules = (
#         # Horizontal por tipo de informacion
#         Rule(
#             LinkExtractor(
#                 allow=r'.*pagina-\d+',
#                 tags=('a'),
#                 attrs=('href')
#             ), follow=True, callback='parse_lojadosuplemento'
#         ),
#     )

#     def parse_lojadosuplemento(self, response):

#         # for link in LinkExtractor().extract_links(response):
#         #     print('result: ', link)

#         # item = ItemLoader(Product(), response)

#         sel = Selector(response)

#         products = sel.xpath("//div[@class='wd-browsing-grid-list   wd-widget-js']/ul/li")

#         for product in products:

#             item = ItemLoader(Product(), product)

#             item.add_xpath('name', './/div[@class="block-1 savings"]/strong/text()')
#             item.add_xpath('price', './/div[@class="block-1 savings"]/strong/text()')
#             item.add_xpath('oldprice', './/div[@class="block-1 savings"]/del/text()')
#             item.add_xpath('image', './/div[@class="variation variation-root"]/img/@src')

#             yield item.load_item()


from time import sleep
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import math
import re
from tqdm import tqdm
import random
import pandas as pd
from utils import *

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()
opts.add_argument("user-agent=" + list_agents[1])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-notifications")

search = choose_search()

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

# # URL origin
url_origin = "https://www.amazon.com.br/s?k={}".format(search)

def set_link(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = "https://www.amazon.com.br/s?k={}".format(
            search
        ) + "&page={}/".format(n)
    return link_pattern

driver.get(url_origin)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="a-section a-spacing-small a-spacing-top-small"]/span'))
)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="a-section a-spacing-small a-spacing-top-small"]/span',
)

print('total_products_string: ', total_products_string)

total_products = get_list_of_numbers([n.text for n in total_products_string][0].replace('.', ''))[-1]

bypage = 60

print('total of products  ', total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)

print("total of clicks: ", total_of_pages)


titles = []
prices = []
oldprices = []
images = []
# unique_prices = []


# lmpm_prices = []

tries = 0

driver.quit()

PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

goTourl = url_origin

while PAGINA_FIN >= PAGINA_INICIO:
    try:

        driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
        driver.get(goTourl)
        driver.implicitly_wait(2)

        list_of_products = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

        print('list_of_products: ', len(list_of_products))

        # WebDriverWait(driver, 20).until(
        #     EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
        # )

        sleep(random.uniform(1.0, 5.0))

        for product in list_of_products:

            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located(
            #         (By.XPATH, '//div[@class="wd-browsing-grid-list   wd-widget-js"]/ul/li//div[@class="variation variation-root"]/img'))
            # )

            try:
                try:
                    title = product.find_element_by_xpath(".//span[@class='a-size-base-plus a-color-base a-text-normal']").text
                    # title = WebDriverWait(product, 5).until(
                    #     EC.presence_of_element_located((By.XPATH, ".//span[@class='a-size-base-plus a-color-base a-text-normal']"))
                    # ).text
                except:
                    title = ''

                try:
                    price = product.find_element_by_xpath('.//span[@data-a-size="l"]//span[@class="a-price-whole"]').text
                    # price = WebDriverWait(product, 5).until(
                    #     EC.presence_of_element_located((By.XPATH, './/span[@data-a-size="l"]//span[@class="a-price-whole"]'))
                    # ).text
                except:
                    price = ''

                try:
                    oldprice = product.find_element_by_xpath('.//span[@class="a-price a-text-price"]/span[@class="a-offscreen"]').text
                except:
                    oldprice = ''

                try:
                    image = product.find_element_by_xpath('.//div[@class="a-section aok-relative s-image-square-aspect"]/img[@class="s-image"]').get_attribute("src")
                except:
                    image = ''

                titles.append(title)
                prices.append(price)
                oldprices.append(oldprice)
                images.append(image)

                print(
                    "Item: ",
                    {
                        "title": title,
                        "price": price,
                        "oldprice": oldprice,
                        "image": image
                    },
                )
            
            except Exception as e:
                print('ERROR')
                print(e)

        try:
            print('current_url: ', driver.current_url)
            # link = driver.find_element_by_xpath('//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]').get_attribute('href')
            link = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]'))
            ).get_attribute('href')
            print(link)
            if PAGINA_INICIO + 1 > PAGINA_FIN:
                break
            print('Go to: ', link)
            goTourl = link
        except Exception as e:
            print(e)
            print('not pages got')
            break

        PAGINA_INICIO += 1

        print('close driver')
        driver.quit()

    except:
        break

driver.close()

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//amazonbr-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//amazonbr-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//amazonbr-{}.xlsx".format(search), index=False)
