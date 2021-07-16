"""
Useful functions to use in all script files
"""

import re
import random
import pandas as pd

def choose_search():
    print('(1) Vitaminas')
    print('(2) Suplementos')
    error = True
    while error:
        try:
            search_input = int(input('Choose only one: '))
            if search_input == 1:
                error = False
                return 'vitaminas'
            if search_input == 2:
                error = False
                return 'suplementos'
        except:
            raise Exception('You should choose between (1) and (2)')

def generate_free_proxy():
    proxies_list = pd.read_csv('list_ips.txt')
    random_ip = random.choice(list(proxies_list))
    return random_ip

def generate_agents():
    list_agents = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36"
    ]
    return random.choice(list_agents)

def get_list_of_numbers(string):
    return [float(s) for s in re.findall(r"-?\d+\.?\d*", string)]
