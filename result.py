# -*- coding: utf-8 -*-

import asyncio
import json
import time
from datetime import datetime
from threading import Thread
from utils import redis_c, load_yaml, DBHelper, md5


class Result:

    def __init__(self, data):
        self.db = DBHelper()
        self.data = data

    def save_db(self):
        pass

    async def process(self):
        data = self.data
        for i in data['start']:
            data_hash = md5(data['raw_url'] + str(i))
            print(data_hash)
            sql = "insert into sec_event (title, start, abstract, source, event_type, raw_url, weight, hash) values \
                ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
                (data['title'].strip(), i, data['abstract'].strip(), \
                 data['source'], data['event_type'], data['raw_url'], \
                 data['weight'], data_hash)
            print(sql)
            a = self.db.execute(sql)
            print(a)


def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    main_loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_thread_loop, args=(main_loop,))
    loop_thread.setDaemon(True)
    loop_thread.start()

    print('-------init result pipeline--------')
    while True:
        result = redis_c.rpop("result")
        if result:
            result = json.loads(result)
            print("start %s" % result)
            r = Result(result)
            asyncio.run_coroutine_threadsafe(r.process(), main_loop)
        time.sleep(3)
