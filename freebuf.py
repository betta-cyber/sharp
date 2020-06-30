# -*- coding: utf-8 -*-


import re
import requests
from bs4 import BeautifulSoup


subject_dict = {u'漏洞':'http://www.freebuf.com/vuls', u'安全工具':'http://www.freebuf.com/sectool',
                u'WEB安全':'http://www.freebuf.com/articles/web', u'系统安全':'http://www.freebuf.com/articles/system',
                u'网络安全':'http://www.freebuf.com/articles/network', u'无线安全':'http://www.freebuf.com/articles/wireless',
                u'终端安全':'http://www.freebuf.com/articles/terminal', u'数据安全':'http://www.freebuf.com/articles/database',
                u'安全管理':'http://www.freebuf.com/articles/security-management', u'企业安全':'http://www.freebuf.com/articles/es',
                u'极客':'http://www.freebuf.com/geek'}


def spider(filename, url):
    page = 0
    error_couter = 0
    while True:
        page += 1
        try:
            html = requests.get(url + '/page/' + str(page))
            code = html.status_code
            if code == 404:
                error_couter += 1
                if error_couter == 1:
                    print("Subject %s may only have %s pages." % (filename, str(page - 1)))
                if error_couter <= 3:
                    print("Retrying %s: 404 not Found!" % str(error_couter))
                    continue
                else:
                    print("Subject %s finished!" % filename)
                    print("#################################")
                    break
            else:
                print(u"Parsing page: " + str(page))
                soup = BeautifulSoup(html.text, 'html.parser')
                site = soup.select('#timeline > div')
                for each in site:
                    print(site)
        except Exception as e:
            print(e)
            pass


def main():
    for key, value in subject_dict.items():
        spider(key, value)


if __name__ == '__main__':
    main()
