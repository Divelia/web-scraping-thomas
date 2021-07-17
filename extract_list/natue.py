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
opts.add_argument("user-agent=" + list_agents[2])
opts.add_argument("--start-maximized")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-notifications")

search = choose_search()

driver = webdriver.Chrome('./chromedriver', chrome_options=opts)


# URL origin
url_origin = "https://www.natue.com.br/{}".format(search)

driver.get(url_origin)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="vtex-search-result-3-x-totalProducts--layout pv5 ph9 bn-ns bt-s b--muted-5 tc-s tl t-action--small"]/span',
)
xx = [n.text for n in total_products_string][0].replace(' ', '').replace('.', '')

print(xx)

total_products = get_list_of_numbers(xx)[0]

bypage = 12

print('total of products  ', total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of clicks: ", total_of_pages)

# for page in tqdm(range(1)):
for page in tqdm(range(1, total_of_pages)):
    try:
        sleep(random.uniform(1.0, 2.0))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        sleep(random.uniform(1.0, 3.0))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer "]'))
        )

        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer "]'))
        )

        driver.execute_script("arguments[0].click();", button)

        # button.click()
    except Exception as e:
        print(e)
        pass


sleep(random.uniform(10.0, 20.0))

list_of_products = driver.find_elements(By.XPATH, '//div[@class="vtex-search-result-3-x-gallery flex flex-row flex-wrap items-stretch bn ph1 na4 pl9-l"]/div')

titles = []
prices = []
oldprices = []
promos = []
images = []

print('total of products to extract: ', len(list_of_products))

for product in list_of_products:
    try:
        try:
            title_list = product.find_elements_by_xpath('.//h1[@class="vtex-product-summary-2-x-productNameContainer mv0 vtex-product-summary-2-x-nameWrapper overflow-hidden c-on-base f5"]/span')
            title = [n.text for n in title_list][0]
        except:
            title = ''
        try:
            price = product.find_element_by_xpath('.//div[@class="vtex-store-components-3-x-sellingPrice vtex-store-components-3-x-sellingPriceContainer vtex-product-summary-2-x-sellingPriceContainer pt1 pb3 c-on-base vtex-product-summary-2-x-price_sellingPriceContainer"]//span[@class="vtex-product-summary-2-x-currencyContainer"]').text
        except:
            price = ''
        try:
            oldprice = product.find_element_by_xpath('.//div[@class="vtex-store-components-3-x-listPrice vtex-product-summary-2-x-listPriceContainer pv1 normal c-muted-2 vtex-product-summary-2-x-price_listPriceContainer"]//span[@class="vtex-product-summary-2-x-currencyContainer"]').text
        except:
            oldprice = ''
        try:
            image = product.find_element_by_xpath('.//img[@class="vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image"]').get_attribute("src")
        except:
            image = ''
        try:
            promo_list = product.find_elements_by_xpath('.//div[@class="vtex-store-components-3-x-installmentsPrice vtex-product-summary-2-x-installmentContainer t-small-ns c-muted-2 vtex-product-summary-2-x-price_installmentContainer"]/span')
            xx = [n.text for n in promo_list]
            promo = ' '.join(xx)
        except:
            promo = ''

        titles.append(title)
        prices.append(price)
        oldprices.append(oldprice)
        images.append(image)
        promos.append(promo)

        print(
            "Item: ",
            {
                "title": title,
                "price": price,
                "oldprice": oldprice,
                "image": image,
                "promo": promo
            },
        )

    except Exception as e:
        print(e)

driver.close()

dicts = {}

dicts["name"] = titles
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["image"] = images
dicts["promo"] = promos

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//natue-{}.xlsx".format(search))
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//natue-{}.xlsx".format(search), index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//natue-{}.xlsx".format(search), index=False)

