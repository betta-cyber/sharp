# -*- coding: utf-8 -*-

import asyncio
import time
from pyppeteer import launch
from bs4 import BeautifulSoup
from utils import DBHelper


async def clawer(u):
    browser = await launch(headless=False)
    page = await browser.newPage()
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
    await page.setViewport({'width': 1080, 'height': 960})

    await page.goto(u['url'])
    await page.evaluate("""
            () =>{
                   Object.defineProperties(navigator,{
                     webdriver:{
                       get: () => false
                     }
                   })
            }
        """)

    content = await page.content()

    data = BeautifulSoup(content, "html.parser")
    cal_lists = data.select('body > div.container > div > div > div > div > table > tbody > tr')

    # init db
    mysql_db = DBHelper()
    for c in cal_lists:
        title_dom = c.find('a', class_="vul-title")
        time_dom = c.find('td', class_="datetime")
        title = title_dom.get_text()
        start = time_dom.get_text()
        level_dom = c.find('div', class_="vul-level")
        level = level_dom['data-original-title']
        raw_url = "https://www.seebug.org" + title_dom['href']
        ssv_id = c.find('a').get_text()
        print(title, start, level, raw_url, ssv_id)

        # page = await browser.newPage()
        # await page.goto(raw_url)
        # page_content = await page.content()

        # page_data = BeautifulSoup(page_content, "html.parser")
        # bodylabel = page_data.select('#new_content > p')
        # abstract = " ".join([x.get_text() for x in bodylabel])
        # abstract = abstract.strip()[:200]
        # await page.close()

        sql = "insert into vul (title, summary, commit_time, ssv_id, level, raw_url, cve_id) values \
            ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (title, '', start, ssv_id, level, raw_url, '')
        # print(sql)
        a = mysql_db.execute(sql)
        print(a)

    # next_page = int(current_page) + 1
    # if next_page <= int(total_page):
        # await cac_clawer("https://www.cert.org.cn/publish/main/49/index_%s.html" % next_page)

    await browser.close()


def tc260_clawer():
    clawer_rule = [
        # https://www.cert.org.cn/publish/main/49/index.html
        {
            "url": 'https://www.seebug.org/vuldb/vulnerabilities?order_time=0&order_rank=1&category=&level=all&submitTime=year&has_all=default&has_poc=default&has_vm=default&has_detail=default&has_affect=default',
            "event_type": "新闻动态",
            "source": "信息安全标准化技术委员会",
        },
    ]

    # 此处不需要next page 因为一次性取1000个
    # finish

    for u in clawer_rule:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(clawer(u))


if __name__ == '__main__':
    tc260_clawer()
