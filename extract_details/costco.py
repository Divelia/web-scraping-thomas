from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re

list_agents = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
]
opts = Options()
opts.add_argument("user-agent=" + list_agents[0])

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)

url_origin = "https://www.costco.com.mx/search?text=Vitamina"


def set_url(n):
    if n == 1:
        return url_origin
    else:
        return url_origin + "&page={}".format(n - 1)


driver.get(url_origin)

# total = driver.find_elements(By.XPATH, '//div[@class="cx-sorting top"]/div[@class="search-pagination-container hidden-xs hidden-sm"]/span')

# print('total: ', total)
# print('total: ', total[0].text)

# total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(",", ""))]

# print(total_numbers)

# total = total_numbers[-1]
# print("Total of pages: ", total)

PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

skus = []
titles = []
images = []
brands = []
prices = []
oldprices = []
categories = []
weights = []

while PAGINA_FIN >= PAGINA_INICIO:

    driver.get(set_url(PAGINA_INICIO))

    try:
      btn = driver.find_element(By.XPATH, '//div[@role="group"]/button[@class="btn btn-primary gdpr-accept"]')
      btn.click()
    except:
      pass

    print("going to ...", set_url(PAGINA_INICIO))

    links_productos = driver.find_elements(
        By.XPATH,
        '//ul[@class="product-listing product-grid"]/sip-product-list-item/li/div/a',
    )
    links_de_la_pagina = []

    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    print("Total of links in present page: ", len(links_de_la_pagina))

    for link in links_de_la_pagina:
        print(link)

        try:
            driver.get(link)

            sku = driver.find_element(
                By.XPATH,
                '//div[@class="product-title-container hidden-xs hidden-sm hidden-tablet-landscape col-xs-12 col-sm-12 col-md-6 col-tab-6 "]//span',
            ).text
            title_list = driver.find_elements(By.XPATH, '//h1[@itemprop="name"]')
            title = title_list[0].text
            image = driver.find_element(
                By.XPATH, '//div[@class="item"]//div[@class="zoomImg"]/img'
            ).get_attribute("src")
            price = driver.find_element(
                By.XPATH,
                '//div[@class="price-after-discount"]/span[@class="you-pay-value"]',
            ).text
            try:
                oldprice = driver.find_element(
                    By.XPATH,
                    '//div[@class="price-original"]/span[@class="price-value"]/span',
                ).text
            except:
                oldprice = ""
            categoriy_list = driver.find_elements(
                By.XPATH, '//ol[@class="breadcrumb"]/li/a'
            )
            category = categoriy_list[-1].text

            table = driver.find_elements_by_xpath(
                './/div[@class="product-classifications"]/table/tr'
            )
            print(len(table))

            # search in table for extra information as marca and peso neto
            if table:

                headers = [tr.find_element_by_tag_name("th") for tr in table]
                headers_name = [th.text for th in headers]

                values = [tr.find_element_by_tag_name("td") for tr in table]
                values_name = [td.text for td in values]

                print("headers: ", headers_name)
                print("marca is in ? ")
                if "Marca" in headers_name:
                    indexof = headers_name.index("Marca")
                    brand = values_name[indexof]
                if "Peso neto" in headers_name:
                    indexof = headers_name.index("Peso neto")
                    weight = values_name[indexof]

            print(price)

            # guardar datos
            skus.append(sku)
            titles.append(title)
            images.append(image)
            prices.append(price)
            oldprices.append(oldprice)
            categories.append(category)
            brands.append(brand)
            weights.append(weight)

            print(
                "Item: ",
                {
                    "id": sku,
                    "title": title,
                    "image": image,
                    "price": price,
                    "oldprice": oldprice,
                    "category": category,
                    "brand": brand,
                    "weight": weight,
                },
            )

            driver.back()
        except Exception as e:
            print(e)
            driver.back()

    PAGINA_INICIO += 1

dicts = {}

dicts["ids"] = skus
dicts["name"] = titles
dicts["image"] = images
dicts["price"] = prices
dicts["oldprice"] = oldprices
dicts["category"] = categories
dicts["brand"] = brands
dicts["weight"] = weights

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//costco.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//costco.xlsx")
else:
    df_web.to_excel("outputs//costco.xlsx", index=False)
