# -*- coding: utf-8 -*-

import requests
import time
from bs4 import BeautifulSoup

url = "https://nvd.nist.gov/vuln/full-listing/2020/7"

r = requests.get(url)
soup = BeautifulSoup(r.text, 'html.parser')

lists = soup.select('#page-content > div.row > span')

for l in lists:
    a = l.find('a')
    title_link = "https://nvd.nist.gov/" + a['href']

    requests.get(title_link)

    time.sleep(30)
