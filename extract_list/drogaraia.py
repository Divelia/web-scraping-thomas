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
import math

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
]

opts = Options()
opts.add_argument("user-agent=" + list_agents[2])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-notifications")

search = choose_search()

if search == 'vitaminas':
    url_origin = "https://www.drogaraia.com.br/bem-estar/{}.html".format(search)
else:
    url_origin = "https://busca.drogaraia.com.br/search?w={}".format(search.upper())


print("Going to... ", url_origin)

driver = webdriver.Chrome("./chromedriver", chrome_options=opts)

driver.get(url_origin)

if search == 'vitaminas':
    total = driver.find_element(
        By.XPATH,
        '//div[@class="col-main-before"]//p[@class="amount inline amount--has-pages"]',
    ).text
else:
    total_list = driver.find_elements(
        By.XPATH,
        '//p[@class="amount inline amount--has-pages sli_num_results"]',
    )
    total = total_list[0].text

total_products = get_list_of_numbers(total)[0]
bypage = 24

print("total of products: ", total_products)
print("total of pages. ", math.ceil(total_products / bypage))


def set_url(n):
    if n == 1:
        link_pattern = url_origin
    else:
        if search == 'vitaminas':
            link_pattern = url_origin + "?p={}".format(n)
        else:
            link_pattern = "https://busca.drogaraia.com.br/search?p=Q&srid=S1-4SEA-AWSP&lbc=dr&ts=custom-dr&w=SUPLEMENTOS&uid=939723673&method=and&isort=score&view=grid&srt={}".format(24+24*(t-2))
    return link_pattern


PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

titles = []
prices = []
oldprices = []
unique_prices = []
lmpm_prices = []
images = []
quantities = []

while PAGINA_FIN >= PAGINA_INICIO:

    sleep(random.uniform(1.0, 3.0))

    print("Going to page ... ", PAGINA_INICIO)

    if search == 'vitaminas':
        driver.get(set_url(PAGINA_INICIO))

        products = driver.find_elements(
            By.XPATH,
            '//div[@class="category-products"]/ul/li',
        )
    else:
        products = driver.find_elements(
            By.XPATH,
            '//ul[@class="first last odd sli_container products-grid "]/li'
        )

    print(len(products))

    for product in products:
        try:
            try:
                if search == 'vitaminas':
                    title = product.find_element_by_xpath('.//a[@class="show-hover"]').text
                else:
                    title = product.find_element_by_xpath('.//a[@data-tb-sid="st_title-link"]').text
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
                    product.find_element_by_xpath(
                        './/div[@class="price lmpm-price"]'
                    ).text
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
                        './/span[@class="regular-price"]/span[2]'
                    ).text
                except:
                    price = ""
            try:
                image = product.find_element_by_xpath(
                    './/img[contains(@id, "product-collection-image-")]'
                ).get_attribute("src")
            except:
                image = ""

            try:
                quantity = product.find_element_by_xpath('.//div[@class="product-attributes"]/ul').text.replace('\n', ' ').replace('\r', ' ').strip()
            except:
                quantity = ""

            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            unique_prices.append(unique_price)
            lmpm_prices.append(lmpm_price)
            images.append(image)
            quantities.append(quantity)

            print(" ")
            print(
                "Item: ",
                {
                    "title": title,
                    "price": price,
                    "oldprice": oldprice,
                    "unique_price": unique_price,
                    "lmpm_price": lmpm_price,
                    "image": image,
                    "quantity": quantity
                },
            )

        except Exception as e:
            print(e)
            driver.back()

    if search == 'suplementos':
        next = driver.find_elements_by_xpath(
            './/a[@class="next i-next btn-more sli_next_page"]'
        )
        next[0].click()

    PAGINA_INICIO += 1

driver.close()
dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["unique_price"] = unique_prices
dicts["lmpm_price"] = lmpm_prices
dicts["oldprice"] = oldprices
dicts["image"] = images
dicts["quantity"] = quantities

df_web = pd.DataFrame.from_dict(dicts)

print(df_web)

try:
    df_previous = pd.read_excel("outputs//drogaraia-{}.xlsx".format(search))
except:
    df_previous = None
    pass

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//drogaraia-{}.xlsx".format(search), index=False)
else:
    df_web.to_excel("outputs//drogaraia-{}.xlsx".format(search), index=False)
