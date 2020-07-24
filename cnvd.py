# -*- coding: utf-8 -*-

import asyncio
import time
from pyppeteer import launch
from bs4 import BeautifulSoup
from utils import DBHelper


async def clawer(u):
    browser = await launch(
        headless=False,
        args=['--disable-infobars', '--no-sandbox', '--disable-dev-shm-usage']
    )
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
    cal_lists = data.select('body > div.mw.Main.clearfix > div.blkContainer > div > div:nth-child(2) > table > tbody > tr')
    # print(cal_lists)

    # init db
    mysql_db = DBHelper()
    for c in cal_lists:
        title_dom = c.find('a')
        # time_dom = c.find('a', class_="fr")
        title = title_dom.get_text()
        # start = time_dom.get_text()
        # level_dom = c.find('img')
        # level = level_dom['title']
        raw_url = "https://www.cnvd.org.cn" + title_dom['href']
        # cnnvd_id = c.find('p').get_text()
        # print(title, raw_url)

        try:
            page = await browser.newPage()
            await page.goto(raw_url)
            page_content = await page.content()
            page_data = BeautifulSoup(page_content, "html.parser")

            bodylabel = page_data.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > div.blkContainerSblk > div.blkContainerSblkCon.clearfix > div.tableDiv > table > tbody > tr:nth-child(1) > td:nth-child(2)')
            cnvd_id = bodylabel[0].get_text().strip()

            bodylabel = page_data.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > div.blkContainerSblk > div.blkContainerSblkCon.clearfix > div.tableDiv > table > tbody > tr:nth-child(2) > td:nth-child(2)')
            publish_time = bodylabel[0].get_text().strip()

            bodylabel = page_data.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > div.blkContainerSblk > div.blkContainerSblkCon.clearfix > div.tableDiv > table > tbody > tr:nth-child(3) > td:nth-child(2) > span ')
            level = bodylabel[0].get_text().strip()

            bodylabel = page_data.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > div.blkContainerSblk > div.blkContainerSblkCon.clearfix > div.tableDiv > table > tbody > tr:nth-child(4) > td:nth-child(2)')
            cve_id = bodylabel[0].get_text().strip()

            bodylabel = page_data.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > div.blkContainerSblk > div.blkContainerSblkCon.clearfix > div.tableDiv > table > tbody > tr:nth-child(5) > td:nth-child(2)')
            description = bodylabel[0].get_text().strip()

            bodylabel = page_data.select('body > div.mw.Main.clearfix > div.blkContainer > div.blkContainerPblk > div.blkContainerSblk > div.blkContainerSblkCon.clearfix > div.tableDiv > table > tbody > tr:nth-child(6) > td:nth-child(2)')
            vul_type = bodylabel[0].get_text().strip()

            await page.close()
            print(cnvd_id, publish_time, level, cve_id, description, vul_type)

        except Exception as e:
            print(e)
            pass

        time.sleep(5)

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
        # https://www.cert.org.cn/publish/main/49/index.html
        {
            "url": 'https://www.cnvd.org.cn/flaw/list',
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
