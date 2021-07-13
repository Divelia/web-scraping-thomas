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


# URL origin
url_origin = "https://www.mundoverde.com.br/vitaminas?_q=VITAMINAS&map=ft"

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

        print(
            "Item: ",
            {
                "id" : id,
                "title": title,
                "price": price,
                "oldprice": oldprice,
                "categories": category,
                "image": image,
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

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//mundoverde.xlsx")
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//mundoverde.xlsx", index=False)
else: 
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//mundoverde.xlsx", index=False)

print("total of links collected: ", total_links)
print("total of links collected: ", len(total_links))
