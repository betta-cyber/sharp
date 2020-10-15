# -*- coding: utf-8 -*-

import time
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import redis_c, load_yaml, md5


def event_clawer():
    for i in ['miit', 'cert']:
    # for i in ['miit', 'cac', 'tc260', 'cert', 'djbh']:
        data = {'type': i, 'class': 'event'}
        redis_c.lpush("list", json.dumps(data))
        # time.sleep(300)


def intelligence_clawer():
    print("ti start")
    for i in ['anquanke', 'xz', 'doonsec', 'cnvd', 'seebug', 'freebuf']:
        data = {'type': i, 'class': 'intelligence'}
        redis_c.lpush("list", json.dumps(data))
        # time.sleep(300)


def vul_clawer():
    print("vul start")
    for i in ['cnvd', 'cnnvd']:
        data = {'type': i, 'class': 'vul'}
        redis_c.lpush("list", json.dumps(data))
        # time.sleep(300)


def update_clawer():
    print("vul start")
    for i in ['github', 'postgresql', 'tsrc']:
        data = {'type': i, 'class': 'update'}
        redis_c.lpush("list", json.dumps(data))


if __name__ == '__main__':
    # sched = BlockingScheduler()
    # sched.add_job(intelligence_clawer, 'interval', hours=10)
    # sched.add_job(event_clawer, 'interval', hours=2)

    # sched.start()

    # intelligence_clawer()
    event_clawer()
    # vul_clawer()
