# -*- coding: utf-8 -*-

import redis
import yaml
import pymysql
import requests
import hashlib
from config import AppConfig

redis_config = AppConfig['default']

redis_c = redis.Redis(host=redis_config.REDIS_HOST, \
                      port=redis_config.REDIS_PORT, \
                      password=redis_config.REDIS_PASSWORD, \
                      db=redis_config.REDIS_DB)


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        content = yaml.load(f, Loader=yaml.FullLoader)

    return content


def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()


class DBHelper:
    # 构造函数
    def __init__(self, host='10.1.161.28', user='secapi', pwd='', db='sec_cal'):
        headers = {
            "Authorization": "Bearer s.C3IOnaDCCowv7SCdYuzVnRyR"
        }
        r = requests.get("https://10.1.161.12:8200/v1/database/static-creds/secapi-s-28", headers=headers, verify=False)
        data = r.json()['data']

        self.host = host
        self.user = data['username']
        self.pwd = data['password']
        self.db = db
        self.conn = None
        self.cur = None

    # 连接数据库
    def connectDatabase(self):
        try:
            self.conn = pymysql.connect(self.host, self.user, self.pwd, self.db, charset='utf8')
        except Exception as e:
            print(e)
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
            print(e)
            self.close()
            return False
        return False

    # 用来查询表数据
    def fetchall(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchall()
