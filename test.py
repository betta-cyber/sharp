# -*- coding: utf-8 -*-

import json
from utils import redis_c, load_yaml

# a = {"type": "tc260", "url": "https://www.tc260.org.cn/front/postDetail.html?id=20200527151336"}
# a = {"type": "tc260"}

a = {"type": "djbh", "url": "http://www.djbh.net/webdev/web/HomeWebAction.do?p=getXxgg&id=8a818256725b454501725b74ac6c0006"}

redis_c.lpush("target", json.dumps(a))

# redis_c.lpush("list", json.dumps(a))
