################################################################################
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module is unittest for Mini_Spider.

Authors: lihaopeng(lihaopeng@baidu.com)
Date:    2018/10/09 08:23:06
"""

import os
import re
import unittest

from urllib import request
import mini_spider

class TestMiniSpider(unittest.TestCase):

    def test_init(self):
        spider = mini_spider.MiniSpider("./conf")
        self.assertEqual(spider.header,{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'})
        self.assertEqual(int(spider.conf["thread_count"]), len(spider.threads))
        self.assertTrue(spider.loger is not None)
        self.assertTrue("url_list_file" in spider.conf)
        self.assertTrue(os.path.exists(spider.conf["output_directory"]))

    def test_download(self):
        spider = mini_spider.MiniSpider("./conf")
        url = "http://www.sina.com.cn"

        response = request.urlopen(url)
        html = response.read()
        file_path = spider.conf["output_directory"] + "/" + url.replace(r"/", r"\\")
        self.assertFalse(spider.download(url, html))
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(spider.download(url, html))
        os.remove(file_path)


    def test_wget(self):
        spider = mini_spider.MiniSpider("./conf")
        url = "http://www.sina.com.cn"

        response = request.urlopen(url)
        html = response.read()
        html = html.decode("utf-8")
        self.assertEqual(spider.wget(url), html)
        self.assertEqual(spider.wget(""), None)

    def test_find_links(self):
        spider = mini_spider.MiniSpider("./conf")
        url = "http://www.sina.com.cn"

        response = request.urlopen("http://www.baidu.com")
        html = response.read().decode("utf-8")
        for link in spider.find_links("http://www.baidu.com", html):
            self.assertTrue(re.match(r"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?", url) is not None)


if __name__ == '__main__':
    unittest.main()
