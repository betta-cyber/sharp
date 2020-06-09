# -*- coding: utf-8 -*-

import asyncio
import json
import time
from datetime import datetime
from threading import Thread
from pyppeteer import launch
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml
from module.date_parser import TimeFinder


class Pipeline:

    def __init__(self, target):
        self.target = load_yaml('rule/detail/%s.yml' % target['type'])
        self.url = target['url']
        self.event_type = target['event_type']
        self.result = {}
        self.content = ""

    def __del__(self):
        pass

    async def parser(self):
        browser = await launch(
            headless=True,
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
            if not k or not v:
                raise Exception('config error')
            self.result[k] = self.get_value(v)
        print(self.result)
        redis_c.lpush('result', json.dumps(self.result))

    def get_value(self, selector):
        try:
            if selector['type'] == "static":
                return selector['pattern']
            else:
                if selector['type'] == "system":
                    if selector['pattern'].startswith('$'):
                        if selector['pattern'] == "$url":
                            value = self.url
                        if selector['pattern'] == "$event_type":
                            value = self.event_type
                    else:
                        return ''
                if selector['type'] == "selector":
                    if selector['struct'] == "string":
                        dom = self.content.select(selector['pattern'])
                        value = dom[0].get_text()
                    if selector['struct'] == 'list':
                        # dom = self.content.select(selector['pattern'])
                        # value = dom[0].get_text()
                        # return value
                        pass
                if selector['type'] == "xpath":
                    pass
                if selector['type'] == "func":
                    if selector['pattern'] == 'find_time':
                        text = self.content.get_text()
                        timefinder = TimeFinder(base_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        value = timefinder.find_time(text)
                # todo:
                # other select tool
        except Exception as e:
            print(str(e))
        # filter length
        try:
            value = value[:selector['length']]
        except Exception:
            pass
        return value


def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    main_loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_thread_loop, args=(main_loop,))
    loop_thread.setDaemon(True)
    loop_thread.start()

    print('-------init pipeline--------')
    while True:
        target = redis_c.rpop("target")
        if target:
            target = json.loads(target)
            print("start %s" % target)
            p = Pipeline(target)
            asyncio.run_coroutine_threadsafe(p.parser(), main_loop)
        time.sleep(3)
