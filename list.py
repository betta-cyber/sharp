# -*- coding: utf-8 -*-

import asyncio
import json
from urllib.parse import urlparse
from threading import Thread
from pyppeteer import launch
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml


class Listpipe:

    def __init__(self, target):
        self.list_obj = load_yaml('rule/list/%s.yml' % target['type'])
        self.result = {}
        self.url_info = None
        self.content = ""

    def __del__(self):
        pass

    async def parser(self):
        browser = await launch(
            headless=False,
            args=['--disable-infobars', '--no-sandbox']
        )
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')

        # need get page and pagesize
        # for loop
        self.url_info = urlparse(self.list_obj['url'])

        await page.goto(self.list_obj['url'])
        self.content = await page.content()

        await browser.close()
        await self.analysis()

    async def analysis(self):
        self.content = BeautifulSoup(self.content, 'html.parser')
        list_dom = self.content.find_all('li', class_=self.list_obj['pattern']['list_class'])
        base_url = "%s://%s" % (self.url_info.scheme, self.url_info.netloc)
        for i in list_dom:
            url_dom = i.find('a')
            url = base_url + url_dom['href']
            print(url)

    def get_value(self, selector):
        try:
            if selector['type'] == "text":
                dom = self.content.select(selector['pattern'])
                value = dom[0].get_text()
                return value
            if selector['type'] == "static":
                return selector['pattern']
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
        target = redis_c.rpop("list")
        if target:
            target = json.loads(target)
            p = Listpipe(target)
            asyncio.run_coroutine_threadsafe(p.parser(), new_loop)
