from bs4 import BeautifulSoup
from curl_cffi import requests
from random import randint
from time import sleep
import warnings
warnings.filterwarnings("ignore")

def request_url(url):
    sleep_time = randint(3,5)
    sleep(sleep_time)
    return requests.get(url, impersonate="chrome110", verify=False).content

def get_soup(url):
    html_doc = 0
    content = request_url(url)
    if content is None:
        return -1
    else:
        html_doc = str(content, 'utf-8', 'ignore')

    if html_doc:
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup
    else:
        return -1