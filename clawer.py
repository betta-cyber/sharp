# -*- coding: utf-8 -*-

import time
import json
from utils import redis_c, load_yaml, md5


if __name__ == '__main__':

    while True:
        for i in ['cert', 'tc260', 'cac', 'djbh']:
            data = {'type': i}
            redis_c.lpush("list", json.dumps(data))
            time.sleep(300)
        time.sleep(7200)
