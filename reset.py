# -*- coding: utf-8 -*-

import redis
import requests

headers = {
    "Authorization": "Bearer s.KOmCzhE0ZoTo7MltoBs0eUdS"
}
r = requests.get("https://10.1.161.12:8200/v1/redis/data/soc", headers=headers, verify=False)
data = r.json()['data']['data']

REDIS_HOST = '127.0.0.1'
REDIS_PASSWORD = data['password']
REDIS_PORT = 6379
REDIS_DB = 1


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
r.flushdb()
