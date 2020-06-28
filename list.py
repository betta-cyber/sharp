# -*- coding: utf-8 -*-

import asyncio
import json
import requests
import time
import re
from urllib.parse import urlparse
from threading import Thread
from pyppeteer import launch, errors
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml, md5

COOKIES = {
    'JSESSIONID': 'FFBA83C59236EEF7467EF304848A7BF3.TomcatA',
    '__jsluid_h': 'e6cd73a71ef2fb89ddd612d44898d26f',
    'flashSet': 'ture',
}

HEADERS = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://www.cac.gov.cn',
    'Referer': 'http://www.cac.gov.cn/wlaq/More.htm',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
}


class Listpipe:

    def __init__(self, target):
        self.ltype = target['type']
        self.lclass = target['class']
        self.list_obj = load_yaml('rule/%s/list/%s.yml' % (target['class'], target['type']))
        self.result = {}
        self.url_info = None
        self.content = ""

    def __del__(self):
        pass

    def unique_url(self, url):
        key = "URL_HASH"
        if not redis_c.hget(key, md5(url)):
            redis_c.hset(key, md5(url), 1)
            return True
        return False

    async def intercept_request(self, req):
        """请求过滤"""
        if req.resourceType in ['image', 'media', 'eventsource', 'websocket']:
            await req.abort()
        else:
            await req.continue_()

    async def goto(self, page, url):
        while True:
            try:
                await page.goto(url, {
                    'timeout': 0,
                    'waitUntil': 'networkidle0'
                })
                break
            except (errors.NetworkError, errors.PageError) as ex:
                if 'net::' in str(ex):
                    await asyncio.sleep(10)
                else:
                    raise

    async def parser(self):
        # need get page and pagesize
        # for loop
        # if self.list_obj.get('token'):
            # browser = await launch(
                # headless=True,
                # args=['--disable-infobars', '--no-sandbox']
            # )
            # page = await browser.newPage()
            # await page.setRequestInterception(True)
            # page.on('request', self.intercept_request)
            # await self.goto(page, self.list_obj['base_url'])
            # await asyncio.sleep(2)
            # # await page.goto(self.list_obj['base_url'])
            # try:
                # token = await page.evaluate('''() => {
                    # return {
                        # token: %s
                    # }
                # }''' % self.list_obj['token'])
            # except Exception as e:
                # print(e)
            # print(token)

        for list_obj in self.list_obj:
            if not list_obj['url'].startswith('$'):
                browser = await launch(
                    headless=True,
                    args=['--disable-infobars', '--no-sandbox']
                )
                page = await browser.newPage()
                await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
                self.url_info = urlparse(list_obj['url'])
                await page.goto(list_obj['url'])
                self.content = await page.content()
                await self.analysis(list_obj)
                await browser.close()
            else:
                if list_obj['url'] == "$requests":
                    data = list_obj['data']
                    r = requests.post(data['url'], headers=HEADERS, cookies=COOKIES, data=data['data'], verify=False)
                    self.content = r.json()
                    self.analysis_json(list_obj)

    async def analysis(self, list_obj):
        self.content = BeautifulSoup(self.content, 'html.parser')
        if list_obj['pattern']['type'] == "list":
            if list_obj['pattern'].get('class'):
                list_dom = self.content.find_all('li', class_=list_obj['pattern']['class'])
            elif list_obj['pattern'].get('selector'):
                list_dom = self.content.select(list_obj['pattern']['selector'])
        if list_obj['pattern']['type'] == "table":
            list_dom = self.content.find_all('tr')
        base_url = "%s://%s" % (self.url_info.scheme, self.url_info.netloc)

        for i in list_dom:
            try:
                text = i.get_text()
                base_time = re.search(list_obj['basetime']['pattern'], text).group()

                url_dom = i.find('a')
                try:
                    u = url_dom[list_obj['pattern']['title_key']]
                except Exception:
                    # default href
                    u = url_dom['href']
                try:
                    length = list_obj['pattern']['length'].split(":")
                    if length[0] and length[1]:
                        u = u[int(length[0]):int(length[1])]
                    elif length[0] and not length[1]:
                        u = u[int(length[0]):]
                    elif not length[0] and length[1]:
                        u = u[:int(length[1])]
                except Exception:
                    pass

                url = base_url + u
                if self.unique_url(str(url)):
                    u = {
                        "type": self.ltype,
                        "url": url,
                        "event_type": list_obj['event_type'],
                        "basetime": base_time + " 00:00:00"
                    }
                    redis_c.lpush('target', json.dumps(u))
                    print("push url %s" % url)
            except Exception:
                pass

    def analysis_json(self, list_obj):
        for i in self.content['list']:
            url = i[list_obj['pattern']['key']]
            if self.unique_url(url):
                u = {
                    "type": self.ltype,
                    "url": url,
                    "event_type": list_obj['event_type'],
                    "basetime": i[list_obj['basetime']['key']][:-2]
                }
                redis_c.lpush('target', json.dumps(u))
                print("push url %s" % url)
            else:
                print("exist url %s" % url)


def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_thread_loop, args=(new_loop,))
    loop_thread.setDaemon(True)
    loop_thread.start()

    print('-------init list-------')

    while True:
        target = redis_c.rpop("list")
        if target:
            target = json.loads(target)
            print(target)
            p = Listpipe(target)
            asyncio.run_coroutine_threadsafe(p.parser(), new_loop)
            time.sleep(30)
