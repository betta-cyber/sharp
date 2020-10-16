# -*- coding: utf-8 -*-

import redis
import yaml
import pymysql
import logging
import requests
import hashlib
from datetime import datetime, timedelta
from config import AppConfig

default_config = AppConfig['default']
logging.basicConfig(filename='debug.log', level=logging.INFO)

redis_c = redis.Redis(host=default_config.REDIS_HOST, \
                      port=default_config.REDIS_PORT, \
                      password=default_config.REDIS_PASSWORD, \
                      db=default_config.REDIS_DB)


def get_ws_url():
    return default_config.BROWERLESS_WS


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        content = yaml.load(f, Loader=yaml.FullLoader)

    return content


def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()


def get_today_zero():
    now = datetime.now()
    zero_time = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second, \
                                microseconds=now.microsecond)
    return zero_time.strftime('%Y-%m-%d %H:%M:%S')


class DBHelper:
    # 构造函数
    def __init__(self, db='sec_web'):
        headers = {
            "Authorization": "Bearer s.h4QW7bEW3vP8e7h0WjNSph7V"
        }
        r = requests.get("https://10.1.161.12:8200/v1/database/static-creds/mysql-29-secapi-s", headers=headers, verify=False)
        data = r.json()['data']

        # self.host = '10.1.161.29'
        # self.user = data['username']
        # self.pwd = data['password']
        self.host = '10.1.30.29'
        self.user = 'root'
        self.pwd = 'root'

        # self.db = db
        self.db = 'eye'
        self.conn = None
        self.cur = None

    # 连接数据库
    def connectDatabase(self):
        try:
            self.conn = pymysql.connect(self.host, self.user, self.pwd, self.db, charset='utf8')
        except Exception as e:
            logging.info("connect mysql %s" % e)
            return False
        self.cur = self.conn.cursor()
        return True

    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    # 执行数据库的sq语句,主要用来做插入操作
    def execute(self, sql, params=None):
        # 连接数据库
        self.connectDatabase()
        try:
            if self.conn and self.cur:
                # 正常逻辑，执行sql，提交操作
                self.cur.execute(sql, params)
                self.conn.commit()
                return True
        except Exception as e:
            logging.info("execute mysql %s" % e)
            self.close()
            return False
        return False

    # 用来查询表数据
    def fetchall(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchall()
