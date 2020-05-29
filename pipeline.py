# -*- coding: utf-8 -*-

import asyncio
import json
from threading import Thread
from pyppeteer import launch
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml


class Pipeline:

    def __init__(self):
        self.target = {}

    async def parser(self, target):
        browser = await launch(
            headless=False,
            args=['--disable-infobars', '--no-sandbox']
        )
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
        # await page.setViewport({'width': 1080, 'height': 960})
        await page.goto(target['url'])
        content = await page.content()

        await browser.close()
        await self.analysis(content)

    async def analysis(self, html):
        data = BeautifulSoup(html, 'html.parser')
        rule = load_yaml('rule/tc260.yml')

        title_dom = data.select(rule['title'])
        self.target['title'] = title_dom[0].get_text()
        abstract_dom = data.select(rule['abstract'])
        self.target['abstract'] = abstract_dom[0].get_text()

        print(self.target)


def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_thread_loop, args=(new_loop,))
    loop_thread.setDaemon(True)
    loop_thread.start()

    p = Pipeline()
    while True:
        target = redis_c.rpop("target")
        if target:
            target = json.loads(target)
            asyncio.run_coroutine_threadsafe(p.parser(target), new_loop)
