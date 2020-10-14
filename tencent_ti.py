# -*- coding: utf-8 -*-

import asyncio
import time
from pyppeteer import launch, connect
from bs4 import BeautifulSoup
from utils import DBHelper, md5
import pymysql


async def clawer(u):
    # browser = await launch(headless=False)
    browser = await connect({"browserWSEndpoint": 'ws://10.1.161.29:3000'})
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

        title_dom = page_data.select('body > div.container.container-user > div > div.section.section-user > div > div > h2')
        title = title_dom[0].get_text().strip()

        platform_dom = page_data.select('body > div.container.container-user > div > div.section.section-user > div > div > div.ti-title-info > div > p > span:nth-child(1)')
        platform = platform_dom[0].get_text().strip()

        bodylabel = page_data.select('body > div.container.container-user > div > div.section.section-user > div > div > div:nth-child(6) > div')
        abstract = bodylabel[0].get_text().strip()
        abstract = pymysql.escape_string(abstract)

        source_dom = page_data.select('body > div.container.container-user > div > div.section.section-user > div > div > div:nth-child(4) > div')
        source = source_dom[0].get_text().strip()

        update_title_dom = page_data.select('body > div.container.container-user > div > div.section.section-user > div > div > div:nth-child(5) > div')
        update_title = update_title_dom[0].get_text().strip()

        cve_dom = page_data.select('body > div.container.container-user > div > div.section.section-user > div > div > div:nth-child(8) > div')
        cve_id = cve_dom[0].get_text().strip()
        # abstract = abstract.strip()[:200]
        await page.close()
        try:
            sql = "insert into update_message (name, component, commit_time, update_type, description, source, cve_id, version, level, source_hash, source_platform, commit_user, update_title) values \
                ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
                (title, component, commit_time, update_type, abstract, source, cve_id, version, vul_type, md5(source + abstract), platform, 'TSRC', update_title)
            # print(sql)
            a = mysql_db.execute(sql)
            print(a)
        except Exception as e:
            print(str(e))

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
