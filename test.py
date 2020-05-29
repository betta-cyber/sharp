# -*- coding: utf-8 -*-

import json
from utils import redis_c, load_yaml

a = {"url": "https://www.tc260.org.cn/front/postDetail.html?id=20200527151336"}

redis_c.lpush("target", json.dumps(a))
