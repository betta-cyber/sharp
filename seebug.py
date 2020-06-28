# -*- coding: utf-8 -*-

import requests
import feedparser
import time
from utils import redis_c, load_yaml, DBHelper, md5

db = DBHelper()

rss = feedparser.parse('https://paper.seebug.org/rss/')

for d in rss.entries:
    print(d)
    raw_url = d.link
    rhash = md5(raw_url)
    publish_time = time.strftime("%Y-%m-%d %H:%M", d.published_parsed)
    sql = "insert into intelligence (title, summary, raw_url, source, publish_time, rhash) values \
        ('%s', '%s', '%s', '%s', '%s', '%s');" % \
        (d.title.strip(), d.summary.strip(), \
         raw_url, "seebug", publish_time, rhash)
    print(sql)
    a = db.execute(sql)
    print(a)
