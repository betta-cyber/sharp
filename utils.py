# -*- coding: utf-8 -*-

import redis
from config import AppConfig

redis_config = AppConfig['default']
print(redis_config.REDIS_PASSWORD)

redis_c = redis.Redis(host=redis_config.REDIS_HOST, \
                      port=redis_config.REDIS_PORT, \
                      password=redis_config.REDIS_PASSWORD, \
                      db=redis_config.REDIS_DB)
