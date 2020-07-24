# -*- coding: utf-8 -*-

import json
from utils import redis_c, load_yaml

# a = {"type": "tc260", "url": "https://www.tc260.org.cn/front/postDetail.html?id=20200527151336"}
# a = {"type": "cac"}
a = {"type": "cnvd", "class": "vul"}

# a = {"type": "djbh", "url": "http://www.djbh.net/webdev/web/HomeWebAction.do?p=getXxgg&id=8a8182566ed3d102016fa6d2737f0034", "event_type": "法文法规"}
# a = {"type": "tc260", "url": "https://www.tc260.org.cn/front/postDetail.html?id=20200527151336", "event_type": "法文法规"}

# redis_c.lpush("target", json.dumps(a))

redis_c.lpush("list", json.dumps(a))
