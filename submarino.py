from selenium import webdriver
from selenium.webdriver.common.by import By
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

url_origin = "https://www.submarino.com.br/busca/vitamina?rc=VITAMINA"


def set_url(n):
    if n == 1:
        return url_origin
    else:
        return url_origin + "&limit=24&offset={}".format(24 * (n - 1))

driver.get(url_origin)

total = driver.find_element(
    By.XPATH, '//span[@class="full-grid__TotalText-fvrmdp-2 BPXil"]'
).text
total_numbers = [float(s) for s in re.findall(r"-?\d+\.?\d*", total.replace(".", ""))]
total = total_numbers[0]
print("Total of products found: ", total)

bypage = 24
if total % bypage == 0:
    TOTAL_PAGES = int(total // bypage)
else:
    TOTAL_PAGES = int(total // bypage + 1)

print("Total of pages: ", TOTAL_PAGES)

PAGINA_INICIO = int(input("Extraer datos desde pagina: "))
PAGINA_FIN = int(input("Extraer datos hasta pagina: "))

skus = []
titles = []
images = []
prices = []
oldprices = []
categories = []

while PAGINA_FIN >= PAGINA_INICIO:

    driver.get(set_url(PAGINA_INICIO))

    print("go to ... ", set_url(PAGINA_INICIO))

    links_productos = driver.find_elements(
        By.XPATH,
        '//div[@class="grid__StyledGrid-sc-1man2hx-0 iFeuoP"]/div//a',
    )

    links_de_la_pagina = []
    for a_link in links_productos:
        links_de_la_pagina.append(a_link.get_attribute("href"))

    print("Total of links in present page: ", len(links_de_la_pagina))

    for link in links_de_la_pagina:

        try:
            driver.get(link)

            try:
                title = (
                    driver.find_element(
                        By.XPATH,
                        '//span[@class="src__Text-sc-154pg0p-0 src__Title-sc-1xq3hsd-0 jccmLy"]',
                    )
                    .text.replace("\n", "")
                    .replace("\t", "")
                )
            except:
                title = ""

            try:
                price_list = driver.find_elements(
                    By.XPATH,
                    '//div[@class="src__BestPrice-sc-1jnodg3-5 ykHPU priceSales"]',
                )
                price = price_list[-1].text.replace("\n", "").replace("\t", "")
            except:
                price = ""

            try:
                oldprice_list = driver.find_elements(
                    By.XPATH, '//span[@class="src__ListPrice-sc-1jnodg3-2 kiFAcL"]'
                )
                oldprice = oldprice_list[-1].text.replace("\n", "").replace("\t", "")
            except:
                oldprice = ""

            try:
                category_list = driver.find_elements(
                    By.XPATH, '//ul[@class="src__List-sc-11934zu-1 fcfLTe"]/li/a'
                )
                category = category_list[-1].text.replace("\n", "").replace("\t", "")
            except:
                category = ""

            try:
                image_list = driver.find_elements(
                    By.XPATH, '//picture[@class="src__Picture-xr9q25-2 fYTOXR"]/img'
                )
                image = image_list[0].text.replace("\n", "").replace("\t", "")
            except:
                image = ""

            sku = link[25:34]

            # guardar datos
            skus.append(sku)
            titles.append(title)
            prices.append(price)
            oldprices.append(oldprice)
            categories.append(category)
            images.append(image)

            print(
                "Item: ",
                {
                    "id": sku,
                    "title": title,
                    "image": image,
                    "price": price,
                    "oldprice": oldprice,
                    "category": category,
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

df_web = pd.DataFrame.from_dict(dicts)
print(df_web)

try:
    df_previous = pd.read_excel("outputs//fahorro.xlsx")
except:
    df_previous = None
    pass

if df_previous is not None:
    df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
    df_all_rows.to_excel("outputs//fahorro.xlsx", ignore_index=True)
else:
    df_web.to_excel("outputs//fahorro.xlsx", index=False)
