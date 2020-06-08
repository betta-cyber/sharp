# -*- coding: utf-8 -*-

import redis
import yaml
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
