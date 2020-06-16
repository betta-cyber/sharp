# -*- coding: utf-8 -*-

import time
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import redis_c, load_yaml, md5


def clawer():
    for i in ['cac', 'tc260', 'cert', 'djbh']:
        data = {'type': i}
        redis_c.lpush("list", json.dumps(data))
        time.sleep(300)


if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(clawer, 'cron', hour=0)
