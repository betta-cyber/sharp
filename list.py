# -*- coding: utf-8 -*-

import asyncio
import json
import requests
import time
import logging
import feedparser
import re
from urllib.parse import urlparse
from threading import Thread
from pyppeteer import launch, errors, connect
from bs4 import BeautifulSoup
from utils import redis_c, load_yaml, md5, get_ws_url
from config import AppConfig

logging.basicConfig(filename='debug.log', level=logging.INFO)
default_config = AppConfig['default']


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
    'Origin': 'http://www.cac.gov.cn', 'Referer': 'http://www.cac.gov.cn/wlaq/More.htm',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
}

GITHUB_HEADERS = {
    'Accept': 'application/vnd.github.v3+json',
}


class Listpipe:

    def __init__(self, target):
        self.ltype = target['type']
        self.lclass = target['class']
        self.list_obj = load_yaml('rule/%s/list/%s.yml' % (target['class'], target['type']))
        self.current_obj = None
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
        logging.info('-- START PARSER LIST --')
        logging.debug(self.list_obj)

        if self.lclass == "intelligence":
            for list_obj in self.list_obj:
                if not list_obj['url'].startswith('$'):
                    if list_obj['data-format'] == "html":
                        if default_config.DEBUG:
                            browser = await launch(
                                headless=False,
                                args=['--disable-infobars', '--no-sandbox']
                            )
                        else:
                            browser = await connect(
                                {"browserwsendpoint": 'ws://%s' % get_ws_url()}
                            )
                        page = await browser.newPage()
                        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
                        self.url_info = urlparse(list_obj['url'])
                        await page.goto(list_obj['url'])
                        self.content = await page.content()
                        self.content = BeautifulSoup(self.content, 'html.parser')
                        await browser.close()
                        self.analysis_html(list_obj)
                    elif list_obj['data-format'] == "rss":
                        rss = feedparser.parse(list_obj['url'])
                        self.content = rss.entries
                        self.analysis_rss(list_obj)
                else:
                    if list_obj['url'] == "$requests":
                        data = list_obj['data']
                        r = requests.get(data['url'])
                        if list_obj['data-format'] == "json":
                            self.content = r.json()
                            self.analysis_json(list_obj)
                        if list_obj['data-format'] == "html":
                            soup = BeautifulSoup(r.text, 'html.parser')
                            self.content = soup
                            self.analysis_html(list_obj)

        elif self.lclass == "event":
            logging.info(' -- event -----')
            for list_obj in self.list_obj:
                if not list_obj['url'].startswith('$'):
                    if default_config.DEBUG:
                        browser = await launch(
                            headless=true,
                            args=['--disable-infobars', '--no-sandbox', '--disable-dev-shm-usage']
                        )
                    else:
                        browser = await connect(
                            {"browserwsendpoint": 'ws://%s' % get_ws_url()}
                        )
                    page = await browser.newPage()
                    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
                    self.url_info = urlparse(list_obj['url'])
                    await page.goto(list_obj['url'])
                    logging.info(' -- finish get url -----')
                    self.content = await page.content()
                    await self.analysis(list_obj)
                    await browser.close()
                else:
                    if list_obj['url'] == "$requests":
                        data = list_obj['data']
                        r = requests.post(data['url'], headers=HEADERS, cookies=COOKIES, data=data['data'], verify=False)
                        self.content = r.json()
                        self.analysis_json(list_obj)

        elif self.lclass == "update":
            logging.info(' -- update info -----')
            for list_obj in self.list_obj:
                if not list_obj['url'].startswith('$'):
                    if default_config.DEBUG:
                        browser = await launch(
                            headless=False,
                            args=['--disable-infobars', '--no-sandbox']
                        )
                    else:
                        browser = await connect(
                            {"browserWSEndpoint": 'ws://%s' % get_ws_url()}
                        )
                    page = await browser.newPage()
                    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
                    self.url_info = urlparse(list_obj['url'])
                    await page.goto(list_obj['url'])
                    logging.info(' -- finish get url -----')
                    self.content = await page.content()
                    await self.analysis_html(list_obj)
                    await browser.close()
                else:
                    if list_obj['url'] == "$requests":
                        # 采用requests 进行发包
                        # 获取json格式数据解析。
                        # 分析json数据的通常都直接过去
                        data = list_obj['data']
                        self.url_info = data['url']
                        r = requests.get(data['url'], headers=GITHUB_HEADERS, verify=False)
                        self.content = r.json()
                        self.analysis_json(list_obj)

        elif self.lclass == "vul":
            logging.info(' -- vul info -----')
            for list_obj in self.list_obj:
                if not list_obj['url'].startswith('$'):
                    if list_obj['data-format'] == "html":
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
                        self.url_info = urlparse(list_obj['url'])
                        await page.goto(list_obj['url'])
                        self.content = await page.content()
                        self.content = BeautifulSoup(self.content, 'html.parser')
                        logging.info(self.content)
                        await browser.close()
                        self.analysis_html(list_obj)

    async def analysis(self, list_obj):
        logging.info('-- analysis event --')
        self.content = BeautifulSoup(self.content, 'html.parser')
        if list_obj['pattern']['type'] == "list":
            if list_obj['pattern'].get('class'):
                list_dom = self.content.find_all('li', class_=list_obj['pattern']['class'])
            elif list_obj['pattern'].get('selector'):
                list_dom = self.content.select(list_obj['pattern']['selector'])
        if list_obj['pattern']['type'] == "table":
            list_dom = self.content.find_all('tr')
        if list_obj['pattern']['type'] == "h2":
            if list_obj['pattern'].get('class'):
                list_dom = self.content.find_all('h2', class_=list_obj['pattern']['class'])
            else:
                list_dom = self.content.find_all('h2')

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
                u = {
                    "class": self.lclass,
                    "type": self.ltype,
                    "url": url,
                    "event_type": list_obj['event_type'],
                    "basetime": base_time + " 00:00:00"
                }
                if self.unique_url(str(url)):
                    redis_c.lpush('target', json.dumps(u))
                    logging.info('-- push url %s --' % url)
                else:
                    logging.error('-- exist url %s --' % url)
            except Exception:
                pass

    # 分析结构直接入库
    def analysis_json(self, list_obj):
        logging.info('-- analysis json --')
        if self.lclass == "intelligence":
            for i in self.content[list_obj['pattern']['selector']]:
                u = {
                    "class": self.lclass,
                    "raw_url": self.get_value(i, list_obj['response']['raw_url']),
                    "title": self.get_value(i, list_obj['response']['title']).strip(),
                    "summary": self.get_value(i, list_obj['response']['summary']),
                    "publish_time": self.get_value(i, list_obj['response']['publish_time']),
                    "source": self.get_value(i, list_obj['response']['source'])
                }
                url = u['raw_url']
                uhash = str(md5(url))
                if self.unique_url(url):
                    u["rhash"] = uhash
                    redis_c.lpush('result', json.dumps(u))
                    logging.info('-- push url %s --' % url)
                else:
                    logging.error('-- exist url %s --' % url)

        elif self.lclass == "event":
            for i in self.content['list']:
                url = i[list_obj['pattern']['key']]
                if self.unique_url(url):
                    u = {
                        "class": self.lclass,
                        "type": self.ltype,
                        "url": url,
                        "event_type": list_obj['event_type'],
                        "basetime": i[list_obj['basetime']['key']][:-2]
                    }
                    redis_c.lpush('target', json.dumps(u))
                    logging.info('-- push url %s --' % url)
                else:
                    logging.error('-- exist url %s --' % url)

        elif self.lclass == "update":
            for i in self.content:
                # logging.info(i)
                # update 组件更新情报的数据结构
                u = {
                    "class": self.lclass,
                    "raw_url": self.get_value(i, list_obj['response']['url']),
                    "component": self.get_value(i, list_obj['response']['component']),
                    "commit_time": self.get_value(i, list_obj['response']['commit_time']),
                    "description": self.get_value(i, list_obj['response']['description']),
                    "source": self.get_value(i, list_obj['response']['source']),
                    "update_type": self.get_value(i, list_obj['response']['update_type']),
                    "cve_id": self.get_value(i, list_obj['response']['cve_id']),
                    "version": self.get_value(i, list_obj['response']['version']),
                    "level": self.get_value(i, list_obj['response']['level']),
                    "source_platform": self.get_value(i, list_obj['response']['source_platform']),
                    "commit_user": self.get_value(i, list_obj['response']['commit_user']),
                    "update_title": self.get_value(i, list_obj['response']['update_title']),
                }
                url = u['raw_url']
                if self.unique_url(url):
                    uhash = str(md5(url))
                    u["source_hash"] = uhash
                    redis_c.lpush('result', json.dumps(u))
                    logging.info('-- push url %s --' % url)
                else:
                    logging.error('-- exist url %s --' % url)

    def analysis_html(self, list_obj):
        logging.info('-- analysis html --')
        try:
            self.content = BeautifulSoup(self.content, 'html.parser', from_encoding='utf-8')
        except Exception as e:
            logging.error(' -- class: %s type: %s BeautifulSoup error %s -----' % (self.lclass, self.ltype, e))
        if self.lclass == "intelligence":
            lists = self.content.select(list_obj['pattern']['selector'])
            self.current_obj = list_obj
            for i in lists:
                # url is the most import thing
                u = {
                    "class": self.lclass,
                    "raw_url": self.get_value(i, list_obj['response']['raw_url']),
                    "title": self.get_value(i, list_obj['response']['title']).strip(),
                    "summary": self.get_value(i, list_obj['response']['summary']),
                    "publish_time": self.get_value(i, list_obj['response']['publish_time']),
                    "source": self.get_value(i, list_obj['response']['source'])
                }
                url = u['raw_url']
                uhash = str(md5(url))
                if self.unique_url(url):
                    u["rhash"] = uhash
                    redis_c.lpush('result', json.dumps(u))
                    logging.info('-- push url %s --' % url)
                else:
                    logging.info('-- exist url %s --' % url)
        if self.lclass == "vul":
            lists = self.content.select(list_obj['pattern']['selector'])
            self.current_obj = list_obj
            for i in lists:
                # url is the most import thing
                u = {
                    "class": self.lclass,
                    "type": self.ltype,
                    "source": self.get_value(i, list_obj['response']['source']),
                    "url": self.get_value(i, list_obj['response']['url']),
                    "title": self.get_value(i, list_obj['response']['title']).strip(),
                }
                url = u['url']
                uhash = str(md5(url))
                if self.unique_url(url):
                    u["rhash"] = uhash
                    redis_c.lpush('target', json.dumps(u))
                    logging.info('-- push url %s --' % url)
        if self.lclass == "update":
            logging.info('-- html update analysis --')
            if list_obj['pattern']['type'] == "h2":
                if list_obj['pattern'].get('class'):
                    lists = self.content.find_all('h2', class_=list_obj['pattern']['class'])
                else:
                    lists = self.content.find_all('h2')
            else:
                lists = self.content.select(list_obj['pattern']['selector'])

            self.current_obj = list_obj
            for i in lists:
                u = {
                    "class": self.lclass,
                    "type": self.ltype,
                    "source": self.get_value(i, list_obj['response']['source']),
                    "url": self.get_value(i, list_obj['response']['url']),
                    "title": self.get_value(i, list_obj['response']['title']).strip(),
                }
                url = u['url']
                uhash = str(md5(url))
                if self.unique_url(url):
                    u["rhash"] = uhash
                    redis_c.lpush('target', json.dumps(u))
                    logging.info('-- push url %s --' % url)
                else:
                    logging.info('-- exist url %s --' % url)

    def analysis_rss(self, list_obj):
        logging.info('-- analysis rss --')
        if self.lclass == "intelligence":
            for i in self.content:
                u = {
                    "class": self.lclass,
                    "raw_url": self.get_value(i, list_obj['response']['raw_url']),
                    "title": self.get_value(i, list_obj['response']['title']).strip(),
                    "summary": self.get_value(i, list_obj['response']['summary']),
                    "publish_time": time.strftime("%Y-%m-%d %H:%M", self.get_value(i, list_obj['response']['publish_time'])),
                    "source": self.get_value(i, list_obj['response']['source'])
                }
                url = u['raw_url']
                uhash = str(md5(url))
                if self.unique_url(url):
                    u["rhash"] = uhash
                    redis_c.lpush('result', json.dumps(u))
                    logging.info('-- push url %s --' % url)

    def get_value(self, data, selector):
        try:
            if selector['type'] == "static":
                return selector['pattern']
            else:
                if selector['type'] == "system":
                    if selector['pattern'].startswith('$'):
                        if selector['pattern'] == "$url":
                            value = self.url_info
                        if selector['pattern'] == "$event_type":
                            value = self.event_type
                    else:
                        return ''
                if selector['type'] == "selector":
                    if selector['struct'] == "string":
                        dom = data.select(selector['pattern'])
                        value = dom[0].get_text()
                    if selector['struct'] == 'list':
                        pass
                if selector['type'] == "find_by_class":
                    d = selector['pattern'].split('|')
                    dom = data.find(d[0], class_=d[1])
                    value = dom.get_text()
                if selector['type'] == "tag":
                    dom = data.find(selector['pattern'])
                    value = dom.get_text()
                if selector['type'] == "key":
                    value = data[selector['pattern']]
                if selector['type'] == "hybrid":
                    value = selector['pattern']
                    matchs = re.findall(r'{(.*)}', selector['pattern'])
                    need_replace = {}
                    for i in matchs:
                        if '.' in i:
                            k = i.split('.')
                            # print(k)
                            dom = self.get_dom(data, k[0])
                            # print(dom)
                            data = dom[k[1]]
                        need_replace[i] = data
                    for key in need_replace.keys():
                        s = "{%s}" % key
                        value = value.replace(s, str(need_replace[key]))
                if selector['type'] == "hybrid-json":
                    value = self.format_url(data, selector['pattern'])
                if selector['type'] == "xpath":
                    pass
                if selector['type'] == "func":
                    if selector['pattern'] == 'filter_time':
                        time_pattern = "\\d{4}-\\d{2}-\\d{2}"
                        value = re.search(time_pattern, data.get_text()).group()
                    if selector['pattern'] == 'get_text':
                        value = data.get_text().strip()
                    if selector['pattern'] == 'check_update_type':
                        pattern = "(?i)payload|security|cve|exp|websec"
                        if re.search(pattern, data['body']):
                            value = "安全更新"
                        else:
                            value = "普通更新"
                    if selector['pattern'] == 'find_cve':
                        cve_pattern = "\\d{4}-\\d{2}-\\d{2}"
                        values = re.findall(cve_pattern, data['body'])
                        value = "\n".join(values)
                # todo:
                # other select tool
        except Exception as e:
            print("get value error %s, key is %s" % (str(e), selector))
        # filter length
        try:
            value = value[:selector['length']]
        except Exception:
            pass
        return value

    def get_dom(self, data, key):
        selector = self.current_obj['response'][key]
        if selector['type'] == "tag":
            dom = data.find(selector['pattern'])
            return dom
        if selector['type'] == "find_by_class":
            d = selector['pattern'].split('|')
            dom = data.find(d[0], class_=d[1])
            return dom

    def format_url(self, data, pattern):
        # print(data, pattern)
        matchs = re.findall(r'{(.*)}', pattern)
        need_replace = {}
        for i in matchs:
            need_replace[i] = data[i]
        for k in need_replace.keys():
            s = "{%s}" % k
            pattern = pattern.replace(s, str(need_replace[k]))
        return pattern


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
            time.sleep(3)
