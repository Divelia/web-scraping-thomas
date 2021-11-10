from bs4 import BeautifulSoup
from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from utils import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import math
from time import sleep
import random

searchx = choose_search()

n = 34

while True:

    if type(searchx) != str:
        try:
            searchx = searchx[n]
        except:
            break
    

    # driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

    # # URL origin
    url_origin = "https://www.amazon.com.br/s?k={}".format(searchx)

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
    driver = webdriver.Chrome('./chromedriver', chrome_options=opts)

    url = url_origin

    print('url: ', url)
    driver.get(url)


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

    PAGINA_INICIO = int(input('Extraer datos desde pagina: '))
    PAGINA_FIN = int(input('Extraer datos hasta pagina: '))


    def get_url(search_term, n):
        if len(search_term.split()) > 1:
            search_term = '+'.join(search_term.split())
        if n == 1:
          return "https://www.amazon.com.br/s?k={}".format(search_term)
        else:
          return "https://www.amazon.com.br/s?k={0}&page={1}&qid=1627023402&ref=sr_pg_{1}".format(search_term, n)

    def extract_record(item):
        # atag = item.h2.a
        # description = atag.text.strip()
        try:
          name = item.find(id="productTitle").text
        except:
          name = ''

        try:
          brand = item.find(id="bylineInfo").text
        except:
          brand = ''

        try:
          price = item.find(id="price_inside_buybox").text
        except:
          price = ''

        try:
          oldprice = item.find("class", "priceBlockStrikePriceString a-text-strike").text
        except:
          oldprice = ''

        # try:
        #   image = item.find('img', 's-image').get('src')
        # except:
        #   image = ''

        # try:
        #   hyperlink = 'https://www.amazon.com.br/' + item.find('a', 'a-link-normal s-no-outline').get('href')
        # except:
        #   hyperlink = ''

        result = [name, brand, price, oldprice]

        return result


    names = []
    brands = []
    prices = []
    oldprices = []
    # images = []
    # hyperlinks = []

    tries = 0


    url = get_url(search, 1)

    m = 0

    for page in range(PAGINA_INICIO, PAGINA_FIN+1):

        try:
            # url = get_url(search, page)

            sleep(random.uniform(5.0, 10.0))
            print('Going to: ', url)

            driver.get(url)

            soup = BeautifulSoup(driver.page_source, 'html.parser')


            while PAGINA_INICIO > m:
              soup = BeautifulSoup(driver.page_source, 'html.parser')
              try:
                next_page = soup.find('ul', 'a-pagination').find('li', 'a-last').find('a').get('href')
              except:
                next_page = soup.find('a', 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator').get('href')

              url = "https://www.amazon.com.br" + next_page
              try:
                driver.get(url)
              except:
                sleep(5)
              m += 1
              print('next_page: ', next_page)

            results = soup.find_all('div', {'data-component-type': 's-search-result'})
            print('len results: ', len(results))

            if len(results) == 0:
              driver.quit()
              opts = Options()
              current_agent = generate_agents()
              opts.add_argument("user-agent={}".format(current_agent))
              current_ip = generate_free_proxy()
              opts.add_argument('--proxy-server={}'.format(current_ip))
              driver = webdriver.Chrome('./chromedriver', chrome_options=opts)
              tries += 1
            if tries > 5:
              break


            url_links = soup.find_all('a', class_="a-link-normal s-no-outline")[1:]
            url_links = [link.get('href') for link in url_links]
            
            for index, item in enumerate(results):

              driver.get(url_links[index])

              soup = BeautifulSoup(driver.page_source, 'html.parser')
              
              record = extract_record(soup)

              if record:
                  print('record: ', record)
                  names.append(record[0])
                  brands.append(record[1])
                  prices.append(record[2])
                  oldprices.append(record[3])
                  # images.append(record[3])
                  # hyperlinks.append(record[4])

                  print(
                      "Item: ",
                      {
                          "name": record[0],
                          "brand": record[1],
                          "price": record[2],
                          "oldprice": record[3],
                          # "image": record[3],
                          # "hyperlink": record[4]
                      },
                  )
            PAGINA_INICIO += 1

        except Exception as e:

            print('last page is: ', url)
            print(e)
            break

    dicts = {}

    dicts["name"] = names
    dicts["brand"] = brands
    dicts["price"] = prices
    dicts["oldprice"] = oldprices
    # dicts["image"] = images
    # dicts["hyperlink"] = hyperlinks

    df_web = pd.DataFrame.from_dict(dicts)

    try:
        df_previous = pd.read_excel("outputs//amazonbr-{}.xlsx".format(search))
        print(df_previous)
    except:
        df_previous = pd.DataFrame()
        pass

    print("is empty: ", df_previous.empty)

    if df_previous.empty:
        df_web.to_excel("outputs//amazonbr2-{}.xlsx".format(search), index=False)
    else:
        df_all_rows = pd.concat([df_previous, df_web], ignore_index=True)
        df_all_rows.to_excel("outputs//amazonbr2-{}.xlsx".format(search), index=False)

    if type(searchx) != str:
        n += 1
    else:
        break
