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
    cal_lists = data.select('body > div.container.container-blog > div > div.section.section-blog > div > div.blog_content > div.content_list > div > div > div.sheet_body > table > tbody > tr')

    # init db
    mysql_db = DBHelper()
    for c in cal_lists:
        dom = c.find_all('td')
        component = dom[0].get_text()
        commit_time = dom[1].get_text()
        update_type = dom[2].get_text()
        version = dom[3].get_text()
        vul_type = dom[4].get_text()
        url_dom = c.find('a')
        # time_dom = c.find('td', class_="datetime")
        # title = title_dom.get_text()
        # start = time_dom.get_text()
        # level_dom = c.find('div', class_="vul-level")
        # level = level_dom['data-original-title']
        raw_url = "https://security.tencent.com/" + url_dom['href']
        # ssv_id = c.find('a').get_text()

        page = await browser.newPage()
        await page.goto(raw_url)
        page_content = await page.content()

        page_data = BeautifulSoup(page_content, "html.parser")
        bodylabel = page_data.select('body > div.container.container-user.container-user-report-detail > div > div.section.section-user > dv > div > diiv:nth-child(5) > div')
        print(bodylabel)
        abstract = bodylabel[0].get_text()

        title_dom = page_data.select('body > div.contaer-user.container-user-report-detail > div > div.section.section-user > d div:nth-child(5) > div')
        title = title_dom[0].get_text().strip()

        cve_dom = page_data.select('body > div.container.container-user.cer-report-detail > div > .section-user > div > div > divv > p > a')
        cve_id = cve_dom[0].get_text().strip()
        # abstract = abstract.strip()[:200]
        await page.close()
        print(abstract, title, cve_id)

        # sql = "insert into vul (title, summary, commit_time, ssv_id, level, raw_url, cve_id) values \
            # ('%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (title, '', start, ssv_id, level, raw_url, '')
        # # print(sql)
        # a = mysql_db.execute(sql)
        # print(a)

    # next_page = int(current_page) + 1
    # if next_page <= int(total_page):
        # await cac_clawer("https://www.cert.org.cn/publish/main/49/index_%s.html" % next_page)

    await browser.close()

def tc260_clawer():
    clawer_rule = [
        {
            "url": 'https://security.tencent.com/ti?appid=0&type=1&level=-1&start_date=&end_date=',
            "event_type": "新闻动态",
            "source": "TSRC",
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
