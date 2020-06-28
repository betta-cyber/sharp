# -*- coding: utf-8 -*-

import requests
from utils import redis_c, load_yaml, DBHelper, md5

db = DBHelper()
a = requests.get("https://api.anquanke.com/data/v1/posts?size=200&page=1")
data = a.json()


for d in data['data']:
    print(d)
    raw_url = "https://www.anquanke.com/post/id/" + str(d['id'])
    rhash = md5(raw_url)
    sql = "insert into intelligence (title, summary, raw_url, source, publish_time, rhash) values \
        ('%s', '%s', '%s', '%s', '%s', '%s');" % \
        (d['title'].strip(), d['desc'].strip(), \
         raw_url, "安全客", d['date'], rhash)
    print(sql)
    a = db.execute(sql)
    print(a)
