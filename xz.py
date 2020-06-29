# -*- coding: utf-8 -*-

import requests
from utils import redis_c, load_yaml, DBHelper, md5

url = "https://xz.aliyun.com/"
db = DBHelper()

r = requests.get(url)
text = r.text


table1 = text.find('<table class="table topic-list">')
table2 = text.find('</table>')
contents = text[table1:table2]
div = contents.split('<tr><td>')


for i in range(1, 31):
    div2 = div[i].split('<a')
    j = 2
    print('-'*50)

    # 取标题
    title1 = div2[j].find('">') + 2
    title2 = div2[j].find('</a>')
    title = div2[j][title1:title2].strip()
    print('标题:'+ title)

    # 取标题连接
    title_link1 = div2[j].find('href="') + 6
    title_link2 = div2[j].find('">')
    title_link = div2[j][title_link1:title_link2]
    print('标题链接为：https://xz.aliyun.com' + title_link)
    j += 2

    # 文章发布时间
    time1 = div2[j].find('/ 2') + 2
    time2 = time1 + 10
    publish_time = div2[j][time1:time2]
    print('该文章发布于:'+ publish_time)

    # 分类
    article_type1 = div2[j].find('">') + 2
    article_type2 = div2[j].find('</a>')
    article_type = div2[j][article_type1:article_type2]
    print('该文章属于:'+ article_type)

    raw_url = 'https://xz.aliyun.com' + title_link
    rhash = md5(raw_url)
    sql = "insert into intelligence (title, summary, raw_url, source, publish_time, rhash) values \
        ('%s', '%s', '%s', '%s', '%s', '%s');" % \
        (title.strip(), title.strip(), \
         raw_url, "先知社区", publish_time, rhash)
    print(sql)
    a = db.execute(sql)
    print(a)
