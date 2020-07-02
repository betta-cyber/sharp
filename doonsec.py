# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml, DBHelper, md5

time_pattern = "\\d{4}-\\d{2}-\\d{2}"
url = "http://wechat.doonsec.com/tags/?page=1&cat_id=3&_=1593596767797"
db = DBHelper()

r = requests.get(url)
data = r.json()


for d in data['data']:
    publish_time = d['publish_time']
    raw_url = d['url']
    rhash = md5(raw_url)
    sql = "insert into intelligence (title, summary, raw_url, source, publish_time, rhash) values \
        ('%s', '%s', '%s', '%s', '%s', '%s');" % \
        (d['title'], d['digest'], \
         raw_url, d['account_name'], publish_time, rhash)
    print(sql)
    a = db.execute(sql)
    print(a)
