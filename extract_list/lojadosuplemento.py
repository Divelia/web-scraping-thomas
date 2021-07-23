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
url_origin = "https://www.lojadosuplemento.com.br/pesquisa?t={}".format(search.upper())

def set_link(n):
    if n == 1:
        link_pattern = url_origin
    else:
        link_pattern = url_origin + "#/pagina-{}".format(n)
    return link_pattern

driver.get(url_origin)

# driver.get('https://www.lojadosuplemento.com.br/')
# driver.implicitly_wait(5)
# driver.find_element(By.XPATH, '//input[@name="t"]').send_keys(search.upper())
# driver.find_element(By.XPATH, '//form[@action="/pesquisa"]/button').click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//div[@class="wrapper text"]//p/strong'))
)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="wrapper text"]//p/strong',
)

print(total_products_string)

total_products = int(get_list_of_numbers(total_products_string[-1].text)[-1])

total_products_bypage = driver.find_elements(
    By.XPATH,
    '//div[@class="wd-browsing-grid-list   wd-widget-js"]/ul/li',
)

bypage = len(total_products_bypage)

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

driver.close()

PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
PAGINA_FIN = int(input('Extraer datos hasta pagina: '))

while PAGINA_FIN >= PAGINA_INICIO:
    try:
        # print('Going to ', set_link(PAGINA_INICIO))
        # driver.get(set_link(PAGINA_INICIO))
        try:
            driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
            driver.get(set_link(PAGINA_INICIO))
        except:
            break

        list_of_products = driver.find_elements(By.XPATH, "//div[@class='wd-browsing-grid-list   wd-widget-js']/ul/li")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='wd-browsing-grid-list   wd-widget-js']/ul/li//div[@class='variation variation-root']/img"))
        )

        sleep(random.uniform(10.0, 15.0))

        for product in list_of_products:


            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="wd-browsing-grid-list   wd-widget-js"]/ul/li//div[@class="variation variation-root"]/img'))
            )

            try:
                try:
                    # title = product.find_element_by_xpath(".//div[@class='name']/a").text
                    title = WebDriverWait(product, 20).until(
                        EC.presence_of_element_located((By.XPATH, ".//div[@class='name']/a"))
                    ).text
                except:
                    title = ''

                try:
                    # price = product.find_element_by_xpath('.//div[@class="block-1 savings"]/strong').text
                    price = WebDriverWait(product, 20).until(
                        EC.presence_of_element_located((By.XPATH, './/div[@class="block-1 savings"]/strong'))
                    ).text
                except:
                    print('wait so much time for price')
                    price = ''

                try:
                    oldprice = product.find_element_by_xpath('.//div[@class="block-1 savings"]/del').text
                except:
                    print('wait so much time for price')
                    oldprice = ''

                try:
                    image = product.find_element_by_xpath('.//div[@class="variation variation-root"]/img').get_attribute("src")
                except:
                    image = ''
                    print('wait so much time for price')

                # try:
                #     unique_price = product.find_element_by_xpath(
                #         './/div[@class="block-2 condition"]/span[1]'
                #     ).text.replace('\n', ' ').replace('\r', ' ').strip()
                # except:
                #     unique_price = ''

                # try:
                #     lmpm_pricex = product.find_elements_by_xpath(".//div[@class='block-2 condition']/span")
                #     lmpm_pricexx = [n.text.replace('\n', ' ').replace('\r', ' ').strip() for n in lmpm_pricex]
                #     lmpm_price = lmpm_pricexx[1] + lmpm_pricexx[2]
                # except:
                #     lmpm_price = ''

                titles.append(title)
                prices.append(price)
                oldprices.append(oldprice)
                images.append(image)
                # unique_prices.append(unique_price)
                # lmpm_prices.append(lmpm_price)

                print(
                    "Item: ",
                    {
                        "title": title,
                        "price": price,
                        "oldprice": oldprice,
                        "image": image,
                        # "unique_price": unique_price,
                        # "lmpm_price": lmpm_price
                    },
                )
            
            except Exception as e:
                print('ERROR')
                print(e)

        try:
            driver.find_element_by_xpath('//div[@id="bio_ep_close"]').click()
        except:
            print('No adverts to close')

        try:
            xx = driver.find_elements_by_xpath('//a[@rel="next"]')
            print('xx: ', xx)
            link = xx[0].get_attribute('href')
            if PAGINA_INICIO + 1 > PAGINA_FIN:
                break
            print('Go to: ', link)
            driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
            driver.get(link)
            driver.implicitly_wait(10)
        except:
            print('not pages got')
            break

        PAGINA_INICIO += 1

        driver.quit()

    except:
        break
        # driver.quit()
        # current_agent = generate_agents()
        # opts.add_argument("user-agent={}".format(current_agent))
        # current_ip = generate_free_proxy()
        # opts.add_argument('--proxy-server={}'.format(current_ip))
        # driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
        # if tries < 5:
        #     driver.quit()
        #     tries += 1
        #     continue
        # else:
        #     print(driver.current_url)
        #     break


driver.close()

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images
# dicts["unique_price"] = unique_prices
# dicts["lmpm_price"] = lmpm_prices

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//lojadosuplemento-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//lojadosuplemento-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//lojadosuplemento-{}.xlsx".format(search), index=False)
