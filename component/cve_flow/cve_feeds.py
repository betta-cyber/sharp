# -*- coding: utf-8 -*-

import requests
import logging
import zipfile
import shutil
from bs4 import BeautifulSoup
from utils import json2tuple_dict, sql_insert

logging.basicConfig(filename='debug.log', level=logging.INFO)


def json_download(fname, url, retry=3, ret=False):
    while retry > 0:
        try:
            logging.info('[+] DOWNLOAD %s to %s %s' % (fname, url, retry))
            r = requests.get(url, stream=True)
            with open('data/json/%s' % fname, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
                retry = retry-1
            with zipfile.ZipFile('data/json/%s' % fname) as zf:
                logging.debug("[+] UNZIP %s" % fname)
                retry = 0
                zf.extractall(path='data/json')
                ret = True
        except Exception as e:
            ret = False
            logging.info("[DOWNLOAD ERROR] %s error:%s" % (url, repr(e)))
    return ret


def cve_monitor(monitor_init=False):

    json_list = []
    if monitor_init:
        pass
    else:
        modified_zip, modified_link = (
            'nvdcve-1.1-modified.json.zip',
            'https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-recent.json.zip'
        )
        json_download(modified_zip, modified_link)
        json_list.extend(['data/json/nvdcve-1.1-recent.json'])

    for j in json_list:
        if "modified" in j:
            # modified json data
            pass

    sql, cve_data = json2tuple_dict(j)
    ret = sql_insert(sql, cve_data)
    logging.info("[+] Parsed %s to database" % j)

if __name__ == '__main__':
    cve_monitor()
