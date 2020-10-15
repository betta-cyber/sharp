# -*- coding: utf-8 -*-

import asyncio
import re
import json
import time
import logging
from datetime import datetime
from threading import Thread
from pyppeteer import launch, connect
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml, get_today_zero, get_ws_url
from module.date_parser import TimeFinder
from module.weight_parser import calculate_weight
from module.vul_component import check_component
from config import AppConfig

logging.basicConfig(filename='debug.log', level=logging.INFO)
default_config = AppConfig['default']


class Pipeline:

    def __init__(self, target):
        self._type = target['type']
        self._class = target['class']
        self._obj = load_yaml('rule/%s/detail/%s.yml' % (target['class'], target['type']))
        self.url = target['url']
        if self._class == "event":
            self.basetime = target.get('basetime', None)
            self.event_type = target['event_type']
        if self._class == "vul":
            self.source = target['source']
        self.result = {}
        self.content = ""

    def __del__(self):
        pass

    async def parser(self):
        logging.info('-- START PARSER DETAIL PAGE --')
        logging.debug(self._obj)

        if self._class == "event":
            if default_config.DEBUG:
                browser = await launch(
                    headless=True,
                    args=['--disable-infobars', '--no-sandbox']
                )
            else:
                browser = await connect(
                    {"browserWSEndpoint": 'ws://%s' % get_ws_url()}
                )
            page = await browser.newPage()
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
            # await page.setViewport({'width': 1080, 'height': 960})
            await page.goto(self.url)
            self.content = await page.content()
            self.content = BeautifulSoup(self.content, 'html.parser')

            await browser.close()
            await self.analysis(self._obj)
        if self._class == "vul":
            if default_config.DEBUG:
                browser = await launch(
                    headless=True,
                    args=['--disable-infobars', '--no-sandbox', '--disable-dev-shm-usage']
                )
            else:
                browser = await connect(
                    {"browserWSEndpoint": 'ws://%s' % get_ws_url()}
                )
            page = await browser.newPage()
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
            await page.setViewport({'width': 1080, 'height': 960})
            await page.goto(self.url)
            self.content = await page.content()
            self.content = BeautifulSoup(self.content, 'html.parser')

            await browser.close()
            await self.analysis_vul(self._obj)

        if self._class == "update":
            if default_config.DEBUG:
                browser = await launch(
                    headless=True,
                    args=['--disable-infobars', '--no-sandbox', '--disable-dev-shm-usage']
                )
            else:
                browser = await connect(
                    {"browserWSEndpoint": 'ws://%s' % get_ws_url()}
                )
            page = await browser.newPage()
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
            await page.setViewport({'width': 1080, 'height': 960})
            await page.goto(self.url)
            self.content = await page.content()
            self.content = BeautifulSoup(self.content, 'html.parser')

            await browser.close()
            await self.analysis_update(self._obj)

    async def analysis(self, obj):
        logging.info('-- START ANALYSIS DETAIL PAGE --')
        for k, v in obj.items():
            if not k or not v:
                raise Exception('config error')
            self.result[k] = self.get_value(v)
        self.result['class'] = "event"
        logging.info('-- FINISH ANALYSIS DETAIL PAGE --')
        logging.info(self.result)
        redis_c.lpush('result', json.dumps(self.result))

    async def analysis_vul(self, obj):
        logging.info('-- START ANALYSIS DETAIL PAGE --')
        for k, v in obj.items():
            if not k or not v:
                raise Exception('config error')
            self.result[k] = self.get_value(v)
        self.result['class'] = "vul"
        self.result['source'] = self.source
        logging.info('-- FINISH ANALYSIS DETAIL PAGE --')
        logging.info(self.result)
        redis_c.lpush('result', json.dumps(self.result))

    async def analysis_update(self, obj):
        logging.info('-- START ANALYSIS UPDATE DETAIL PAGE --')
        for k, v in obj.items():
            if not k or not v:
                raise Exception('config error')
            self.result[k] = self.get_value(v)
        self.result['class'] = "update"
        logging.info('-- FINISH ANALYSIS DETAIL PAGE --')
        logging.info(self.result)
        redis_c.lpush('result', json.dumps(self.result))

    def slice_length(self, u, pattern):
        logging.info("params %s %s" % (u, pattern))
        try:
            length = pattern.split(":")
            if length[0] and length[1]:
                u = u[int(length[0]):int(length[1])]
            elif length[0] and not length[1]:
                u = u[int(length[0]):]
            elif not length[0] and length[1]:
                u = u[:int(length[1])]
        except Exception as e:
            logging.error("slice value error %s" % (str(e)))
        return u

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
                        dom = self.content.select(selector['dom'])
                        text = dom[0].get_text()
                        if self.basetime:
                            timefinder = TimeFinder(base_date=self.basetime)
                        else:
                            timefinder = TimeFinder(base_date=get_today_zero())
                        value = timefinder.find_time(text)
                    if selector['pattern'] == 'get_weight':
                        dom = self.content.select(selector['dom'])
                        text = dom[0].get_text()
                        value = calculate_weight(text)
                    if selector['pattern'] == 'find_cve':
                        dom = self.content.select(selector['dom'])
                        text = dom[0].get_text()
                        cve_pattern = "(?i)cve-\d{3,4}-\d{3,5}"
                        values = re.findall(cve_pattern, text)
                        value = "\n".join(values)
                    if selector['pattern'] == 'find_cnnvd':
                        dom = self.content.select(selector['dom'])
                        text = dom[0].get_text()
                        cnnvd_pattern = "(?i)cnnvd-\d{3,7}-\d{3,5}"
                        values = re.findall(cnnvd_pattern, text)
                        value = "\n".join(values)
                    if selector['pattern'] == 'get_vul_level':
                        dom = self.content.select(selector['dom'])
                        text = dom[0].get_text()
                        if "中" in text:
                            value = "中危"
                        elif "低" in text:
                            value = "低危"
                        elif "高" in text:
                            value = "高危"
                        else:
                            value = text
                    if selector['pattern'] == 'find_component':
                        dom = self.content.select(selector['dom'])
                        text = dom[0].get_text()
                        value = check_component(text)
                # todo:
                # other select tool
        except Exception as e:
            logging.error("get value error %s, key is %s" % (str(e), selector))
            value = ''
        # filter length
        try:
            value = self.slice_length(value, selector['length'])
        except Exception:
            pass
        return value.strip()


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
            logging.info("start %s" % target)
            p = Pipeline(target)
            asyncio.run_coroutine_threadsafe(p.parser(), main_loop)
        time.sleep(1)
