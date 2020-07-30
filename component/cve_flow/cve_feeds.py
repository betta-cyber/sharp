# -*- coding: utf-8 -*-

import requests
import logging
import time
import zipfile
import glob
import shutil
from bs4 import BeautifulSoup
from utils import json2tuple_dict, sql_insert, sql_insert_db
from vul_component import check_component

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
        zips = glob.glob('data/json/nvdcve-1.1-*.json.zip')
        for z in zips:
            with zipfile.ZipFile(z) as zf:
                print("[+] UNZIP %s" % z)
                zf.extractall(path='data/json')

        jsons_stock = glob.glob('data/json/nvdcve-1.1-*.json')
        jsons_stock = [i for i in jsons_stock]
        json_list.extend(jsons_stock)
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
    for c in cve_data:

        time_st = time.strptime(cve_data[c][-4], "%Y-%m-%dT%H:%MZ")
        commit_time = time.strftime('%Y-%m-%d %H:%M', time_st)
        vul_sql = "insert into vulnerability (name, summary, commit_time, level, vul_type, component, source, cve_id) values \
            ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
            (cve_data[c][3], cve_data[c][14],
             commit_time, cve_data[c][-11],
             "", check_component(cve_data[c][14]), "nvd", cve_data[c][3])
        print(vul_sql)
        sql_insert_db(vul_sql)

    logging.info("[+] Parsed %s to database" % j)

if __name__ == '__main__':
    cve_monitor(monitor_init=True)
