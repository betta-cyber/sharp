# -*- coding: utf-8 -*-

import asyncio
import json
import time
import logging
import pymysql
from datetime import datetime
from threading import Thread
from utils import redis_c, load_yaml, DBHelper, md5

logging.basicConfig(filename='debug.log', level=logging.INFO)


class Result:

    def __init__(self, data):
        self.web_db = DBHelper(db="sec_web")
        self.eye_db = DBHelper(db="sec_eye")
        self.data = data

    def save_db(self):
        pass

    async def process(self):
        data = self.data
        if data['class'] == "intelligence":
            sql = "insert into intelligence (title, summary, raw_url, source, publish_time, rhash) values \
                ('%s', '%s', '%s', '%s', '%s', '%s');" % \
                (data['title'].strip(), data['summary'].strip(), \
                 data['raw_url'], data['source'], data['publish_time'], data['rhash'])
            logging.info("sql query %s" % sql)
            a = self.eye_db.execute(sql)
            logging.info("sql query result %s" % a)
        elif data['class'] == "event":
            for i in data['start']:
                data_hash = md5(data['raw_url'] + str(i))
                sql = "insert into sec_event (title, start, abstract, source, event_type, raw_url, weight, hash) values \
                    ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
                    (data['title'].strip(), i, data['abstract'].strip(), \
                     data['source'], data['event_type'], data['raw_url'], \
                     data['weight'], data_hash)
                a = self.web_db.execute(sql)
        elif data['class'] == "update":
            source_hash = md5(data['raw_url'])
            try:
                time_st = time.strptime(data['commit_time'], "%Y-%m-%dT%H:%M:%SZ")
                commit_time = time.strftime('%Y-%m-%d %H:%M', time_st)
            except Exception:
                time_st = time.strptime(data['commit_time'], "%Y-%m-%d %H:%M:%S")
                commit_time = time.strftime('%Y-%m-%d %H:%M', time_st)

            try:
                sql = "insert into update_message (name, component, commit_time, update_type, description, source, cve_id, version, level, source_hash, source_platform, commit_user, update_title) values \
                    ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
                    (data['update_title'].strip(), data['component'].strip(), \
                     commit_time, data['update_type'], pymysql.escape_string(data['description']), \
                     data['source'], data['cve_id'], data['version'], data['level'], \
                     source_hash, data['source_platform'], data['commit_user'], data['update_title'])
                logging.info("sql query %s" % sql)
                a = self.eye_db.execute(sql)
                logging.info("sql query result %s" % a)
            except Exception as e:
                print(e)
                logging.error("sql query error %s" % e)
        elif data['class'] == "vul":
            if data['source'] == "cnvd":
                try:
                    sql = "insert into vulnerability (name, summary, commit_time, level, vul_type, component, source, cve_id, cnvd_id) values \
                        ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
                        (data['title'].strip(), pymysql.escape_string(data['vul_description']),
                         data['publish_time'], data['level'], \
                         data['vul_type'], data['component'], data['source'], \
                         data['cve_id'], data['cnvd_id'])
                    logging.info("sql query %s" % sql)
                    a = self.eye_db.execute(sql)
                    print(a)
                    logging.info("sql query result %s" % a)
                except Exception as e:
                    print(str(e))
            if data['source'] == "cnnvd":
                try:
                    sql = "insert into vulnerability (name, summary, commit_time, level, vul_type, component, source, cve_id, cnnvd_id) values \
                        ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % \
                        (data['title'].strip(), pymysql.escape_string(data['vul_description']),
                         data['publish_time'], data['level'], \
                         data['vul_type'], data['component'], data['source'], \
                         data['cve_id'], data['cnnvd_id'])
                    logging.info("sql query %s" % sql)
                    a = self.eye_db.execute(sql)
                    print(a)
                    logging.info("sql query result %s" % a)
                except Exception as e:
                    print(str(e))



def start_thread_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    main_loop = asyncio.new_event_loop()
    loop_thread = Thread(target=start_thread_loop, args=(main_loop,))
    loop_thread.setDaemon(True)
    loop_thread.start()

    logging.info('-------init result pipeline--------')
    while True:
        result = redis_c.rpop("result")
        if result:
            result = json.loads(result)
            logging.info("start %s" % result)
            r = Result(result)
            asyncio.run_coroutine_threadsafe(r.process(), main_loop)
        time.sleep(3)
