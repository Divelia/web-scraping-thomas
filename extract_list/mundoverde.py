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

# url_origin = "https://www.mundoverde.com.br/{0}?_q={1}&map=ft".format(search, search.upper())

# print("Going to... ", url_origin)

# response = requests.get(url_origin, headers=headers)

# parser = html.fromstring(response.text)

# try:
#     total = parser.xpath(
#         '//div[contains(@class, "t-action--small")]/span/text()'
#     )

#     total_of_products = get_list_of_numbers(total)
#     bypage = 12
#     print("total of poroducts: ", total_of_products)

#     TOTAL_PAGES = math.ceil(total_of_products / bypage)

#     print("Total of pages: ", TOTAL_PAGES)
# except:
#     pass

# print(total)


# def set_link(n):
#     if n == 1:
#         link_pattern = url_origin
#     else:
#         link_pattern = "https://www.mundoverde.com.br/{0}?_q={1}&map=ft".format(search, search.upper()) + "&page={}".format(n)
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
#             response = requests.get(
#                 current_url,
#                 headers=headers,
#                 proxies={
#                     "http": "http://" + str(current_proxy),
#                     "https": "https://" + str(current_proxy),
#                     "ftp": "ftp://" + str(current_proxy),
#                 },
#             )
#         else:
#             response = requests.get(current_url, headers=headers)

#         parser = html.fromstring(response.text)
#         products = parser.xpath("//div[contains(@class, 'vtex-search-result-3-x-gallery')]/div/text()")
#         print(products)
#         # beautiful soup parser
#         # soup = BeautifulSoup(response.text)
#         # products_soup = soup.find_all('div', class_="ui-search-layout__item")

#         for index, product in enumerate(products):
#             try:
#                 title = product.xpath(
#                     './/span[@class="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]/text()'
#                 )[0]
#             except:
#                 title = ""
#             try:
#                 price = (
#                     product.xpath(
#                         './/div[@class="vtex-store-components-3-x-sellingPrice vtex-store-components-3-x-sellingPriceContainer vtex-product-summary-2-x-sellingPriceContainer pt1 pb3 c-on-base vtex-product-summary-2-x-price_sellingPriceContainer"]//span[@class="vtex-product-summary-2-x-currencyContainer"]/text()'
#                     )[0]
#                 )
#             except:
#                 price = ""
#             try:
#                 oldprice = product.xpath(
#                     './/div[@class="vtex-store-components-3-x-listPrice vtex-product-summary-2-x-listPriceContainer pv1 normal c-muted-2 vtex-product-summary-2-x-price_listPriceContainer"]//span[@class="vtex-product-summary-2-x-currencyContainer"]/text()'
#                 )[0]
#             except:
#                 oldprice = ""
#             try:
#                 image = product.xpath(
#                     './/img[@class="vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image"]/@src'
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
#     df_previous = pd.read_excel("outputs//mundoverde-{}.xlsx".format(search))
# except:
#     df_previous = pd.DataFrame()
#     pass

# if df_previous.empty:
#     df_web.to_excel("outputs//mundoverde-{}.xlsx".format(search), index=False)
# else:
#     df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
#     df_all_rows.to_excel("outputs//mundoverde-{}.xlsx".format(search), index=False)


from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
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
opts.add_argument("user-agent=" + list_agents[2])
opts.add_argument("--start-maximized")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)


def set_url(n):
    if n == 1:
        return url_origin
    else:
        return url_origin + "&page={}".format(n)

search = choose_search()

url_origin = "https://www.mundoverde.com.br/{0}?_q={1}&map=ft".format(search, search.upper())


# URL origin
# url_origin = "https://www.mundoverde.com.br/vitaminas?_q=VITAMINAS&map=ft"

driver.get(url_origin)

total_products_string = driver.find_element(
    By.XPATH,
    '//div[@class="vtex-search-result-3-x-totalProducts--layout pv5 ph9 bn-ns bt-s b--muted-5 tc-s tl t-action--small"]/span',
).text
total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total_products_string)]
total_products = total_numbers[0]
print(total_products)

bypage = 12
total_of_pages = math.ceil(total_products / bypage)
print("total of pages ", total_of_pages)

total_links = []

print('obtaining links ...')
for page in tqdm(range(1, total_of_pages)):
    try:
        sleep(random.uniform(1.0, 5.0))

        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="vtex-search-result-3-x-buttonShowMore w-100 flex justify-center"]/button'))
        )
        button.click()

    except Exception as e:
        print(e)
        pass


links_products = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located(
        ((By.XPATH, '//div[@class="vtex-flex-layout-0-x-flexColChild pb0"]//section[contains(@class, "vtex-product-summary")]/a'))
    )
)

# print(len(links_products))
for product in links_products:
    total_links.append(product.get_attribute("href"))

print(len(total_links))

opts.add_argument("user-agent=" + list_agents[1])
opts.add_argument("--start-maximized")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

ids = []
titles = []
prices = []
oldprices = []
categories = []
images = []
hyperlinks = []

for p in total_links:
    driver.get(p)
    try:
        try:
            id = driver.find_element(By.XPATH, '//span[@class="vtex-product-identifier-0-x-product-identifier__value"]').text
        except:
            id = ''
        try:
            title = driver.find_element(By.XPATH, '//h1[@class="vtex-store-components-3-x-productNameContainer mv0 t-heading-4"]').text
        except:
            title = ''
        try:
            prices_list = driver.find_elements(By.XPATH, '//span[@class="vtex-store-components-3-x-currencyContainer"]/span[@class="vtex-store-components-3-x-currencyInteger"]')
            if len(prices_list) == 1:
                price = prices_list[0].text
                oldprice = ''
            else:
                oldprice = prices_list[0].text
                price = prices_list[1].text
        except Exception as e:
            price = 'not available'
            oldprice = 'not available'

        try:
            category_list = driver.find_elements(By.XPATH, '//div[@data-testid="breadcrumb"]//span')
            category_list_text = [n.text for n in category_list]
            category = category_list_text[2]
        except:
            category = ''

        try:
            image_list = driver.find_element(By.XPATH, '//img[@data-vtex-preload="true"]')
            image = image_list.get_attribute("src")
        except:
            image = ''

        ids.append(id)
        titles.append(title)
        oldprices.append(oldprice)
        prices.append(price)
        categories.append(category)
        images.append(image)
        hyperlinks.append(p)

        print(
            "Item: ",
            {
                "id" : id,
                "title": title,
                "price": price,
                "oldprice": oldprice,
                "categories": category,
                "image": image,
                "hyperlink": p
            },
        )

    except Exception as e:
        print(e)
        driver.back()

driver.close()

dicts = {}

dicts["id"] = ids
dicts["title"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["category"] = categories
dicts["image"] = images
dicts["hyperlink"] = hyperlinks

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//mundoverde-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//mundoverde-{}.xlsx".format(search), index=False)
else: 
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//mundoverde-{}.xlsx".format(search), index=False)
