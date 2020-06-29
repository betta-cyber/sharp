# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml, DBHelper, md5

time_pattern = "\\d{4}-\\d{2}-\\d{2}"
url = "https://www.cnvd.org.cn/webinfo/list?type=2"
db = DBHelper()

r = requests.get(url)

soup = BeautifulSoup(r.text, 'html.parser')

print(soup.prettify())

lists = soup.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > table > tbody > tr')

for l in lists:
    # print(l)
    a = l.find('a')
    title = a.get_text().strip()
    title_link = a['href']
    text = l.get_text()

    publish_time = re.search(time_pattern, text).group()
    print(title, publish_time)

    raw_url = 'https://www.cnvd.org.cn/' + title_link
    rhash = md5(raw_url)
    sql = "insert into intelligence (title, summary, raw_url, source, publish_time, rhash) values \
        ('%s', '%s', '%s', '%s', '%s', '%s');" % \
        (title, title, \
         raw_url, "cnvd", publish_time, rhash)
    print(sql)
    a = db.execute(sql)
    print(a)
