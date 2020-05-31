# -*- coding: utf-8 -*-

import asyncio
import json
from threading import Thread
from pyppeteer import launch
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml


class Pipeline:

    def __init__(self, target):
        self.target = load_yaml('rule/%s.yml' % target['type'])
        self.url = target['url']
        self.result = {}
        self.content = ""

    async def parser(self):
        browser = await launch(
            headless=False,
            args=['--disable-infobars', '--no-sandbox']
        )
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
        # await page.setViewport({'width': 1080, 'height': 960})
        await page.goto(self.url)
        self.content = await page.content()

        await browser.close()
        await self.analysis()

    async def analysis(self):
        self.content = BeautifulSoup(self.content, 'html.parser')

        for k, v in self.target.items():
            self.result[k] = self.get_value(v)
        print(self.result)

    def get_value(self, selector):
        try:
            dom = self.content.select(selector)
            value = dom[0].get_text()
            return value
        except Exception as e:
            print(str(e))
            return ""



def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_thread_loop, args=(new_loop,))
    loop_thread.setDaemon(True)
    loop_thread.start()

    while True:
        target = redis_c.rpop("target")
        if target:
            target = json.loads(target)
            p = Pipeline(target)
            asyncio.run_coroutine_threadsafe(p.parser(), new_loop)
