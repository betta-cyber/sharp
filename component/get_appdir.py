# -*- coding: utf-8 -*-

import asyncio
import time
from pyppeteer import launch
from bs4 import BeautifulSoup


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
    print(data)
    cal_lists = data.findAll('li')
    for c in cal_lists:
        a = c.find('a')
        d = a.get_text()
        print(d)

    await browser.close()


def tc260_clawer():
    clawer_rule = [
        # https://www.cert.org.cn/publish/main/49/index.html
        {
            "url": 'https://www.seebug.org/appdir',
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
