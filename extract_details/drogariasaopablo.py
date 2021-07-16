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
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-notifications")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)


# URL origin
url_origin = "https://www.drogariasaopaulo.com.br/pesquisa?q=vitaminas"

driver.get(url_origin)

total_products_string = driver.find_elements(
    By.XPATH,
    '//div[@class="info-pagination"]/span/b',
)

bypage = int(total_products_string[0].text.replace(' ', ''))
total_products = int(total_products_string[1].text.replace(' ', ''))

print('total of products  ',total_products, ' by page: ', bypage)

total_of_pages = math.ceil(total_products / bypage)
print("total of pages ", total_of_pages)

total_links = []

print('obtaining links ...')
for page in tqdm(range(1, total_of_pages)):
    try:
        sleep(random.uniform(1.0, 3.0))

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="text-center btn-load-more"]/button'))
        )

        button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="text-center btn-load-more"]/button'))
        )

        driver.execute_script("arguments[0].click();", button)

        # button.click()

    except Exception as e:
        print(e)
        pass

links_products = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located(
        ((By.XPATH, '//div[@class="vitrine resultItemsWrapper"]//ul/li/a'))
    )
)

# print(len(links_products))
for product in links_products:
    total_links.append(product.get_attribute("href"))

print('total of links products: ', len(total_links))

opts.add_argument("user-agent=" + list_agents[1])
opts.add_argument("--start-maximized")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

ids = []
titles = []
brands = []
prices = []
oldprices = []
categories = []
images = []

for p in total_links:
    driver.get(p)
    try:
        try:
            id = driver.find_element(By.XPATH, '//div[@class="skuReference"]').text
        except:
            id = ''
        try:
            title = driver.find_element(By.XPATH, '//div[contains(@class, "fn productName")]').text
        except:
            title = ''
        try:
            brand = driver.find_element(By.XPATH, '//div[contains(@class, "brandName")]').get_attribute("class").split()[1]
        except:
            brand = ''
        try:
            prices_list = driver.find_elements(By.XPATH, '//p[@class="descricao-preco"]/em//strong[@class="skuBestPrice"]')
            price = prices_list[0].text
        except:
            price = ''
        try:
            oldprices_list = driver.find_elements(By.XPATH, '//p[@class="descricao-preco"]//strong[@class="skuListPrice"]')
            oldprice = oldprices_list[0].text
        except:
            oldprice = ''

        try:
            category_list = driver.find_elements(By.XPATH, '//div[@class="bread-crumb"]/ul/li//span[@itemprop="name"]')
            category_list_text = [n.text for n in category_list]
            category = category_list_text[-1]
        except:
            category = ''

        try:
            image_list = driver.find_element(By.XPATH, '//img[@id="image-main"]')
            image = image_list.get_attribute("src")
        except:
            image = ''

        ids.append(id)
        titles.append(title)
        brands.append(brand)
        prices.append(price)
        oldprices.append(oldprice)
        categories.append(category)
        images.append(image)

        print(
            "Item: ",
            {
                "id" : id,
                "title": title,
                "brand": brand,
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
dicts["brand"] = brands
dicts["oldprice"] = oldprices
dicts["category"] = categories
dicts["image"] = images

df_web = pd.DataFrame.from_dict(dicts)

try:
    df_previous = pd.read_excel("outputs//drogariasaopablo.xlsx")
    print(df_previous)
except:
    df_previous = pd.DataFrame()
    pass

print("is empty: ", df_previous.empty)

if df_previous.empty:
    df_web.to_excel("outputs//drogariasaopablo.xlsx", index=False)
else:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//drogariasaopablo.xlsx", index=False)

print("total of links collected: ", total_links)
print("total of links collected: ", len(total_links))
