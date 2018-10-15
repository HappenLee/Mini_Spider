################################################################################
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
This module provide MiniSpider Class to crawl url data .

Authors: lihaopeng(lihaopeng@baidu.com)
Date:    2018/10/06 17:23:06
"""

import configparser
import re
import logging
import argparse
import chardet
import queue
import urllib.parse
import os
import threading
import time

from urllib import request


class MiniSpider:
    """
    Summary of class here.

    MiniSpider is a class to load conf from local and crawl url by re.

    Attributes:
        header: Camouflage browser head to crawl url
        loger: To log the info of the class.
        conf: Load the conf from local and crawl url by conf
        urls: A queue for crawl task
        threads: A list contains the thread to crawl url
    """

    def __init__(self, conf_path):
        """
        Init the mini_spider by conf.

        Args:
            conf_path: A str of the path of conf
        Returns:
            object of mini_spider
        """
        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}

        log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
        formatter = logging.Formatter(log_fmt)
        log_file_handler = logging.FileHandler("mini_spider.log", mode = "w")
        log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
        log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
        log_file_handler.setFormatter(formatter)
        log_file_handler.setLevel(logging.DEBUG)
        self.loger = logging.getLogger()
        self.loger.addHandler(log_file_handler)

        self.conf = configparser.ConfigParser()
        if not os.path.exists(conf_path):
            self.loger.critical("the conf_path is not exist, program exit.")
            exit(1)
        self.conf.read(conf_path)
        self.conf = self.conf['spider']
        self.urls = queue.Queue()
        self.threads = []

        self.loger.info("open url_list_file to get the url to crawl")
        with open(self.conf["url_list_file"], "r") as file:
            for line in file:
                self.urls.put((line, 0, 0))
        if not os.path.exists(self.conf["output_directory"]):
            self.loger.warning("mkdir the " + self.conf["output_directory"])
            os.makedirs(self.conf["output_directory"])
        for i in range(int(self.conf["thread_count"])):
            self.threads.append(threading.Thread(target=self.crawl))

    def wget(self, url):
        """
        Wget the url from the internet.

        Args:
            url: A str of the url.
        Returns:
            html: The web data of the url.
        Raises:
            socket.timeout: Maybe request will timeout
        """
        if url is not None and len(url) != 0:
            crawl_request = request.Request(url, headers=self.header)
            response = request.urlopen(crawl_request, timeout=int(self.conf["crawl_timeout"]))
            html = response.read()
            charset = chardet.detect(html)
            if charset["encoding"]:
                html = html.decode(charset["encoding"])
            return html
        return None

    def find_links(self, url, html):
        """
        Find the correct link we need by re.

        Args:
            url: A str of the url be crawled.
            html: The html data of the url.
        Returns:
            links: A iterator of links consistent with regular expression rules.
        """
        href_links = re.findall(r'href=["\'](.*?)["|\']', html)
        src_links = re.findall(r'src=["\'](.*?)["|\']', html)
        links = href_links + src_links
        links = filter(lambda link: len(link) > 1 and "java" not in link and ".css" not in link and ".js" not in link,
                       links)
        links = map(lambda link: "http:" + link if not "http" in link and "//" in link else link, links)
        links = map(lambda link: urllib.parse.urljoin(url, link) if link[0] == "/" else link, links)

        return links

    def crawl(self):
        """
        crawl fuction execute by thread.

        Raises:
            Exception: All the probable exception of crawl.
        """
        self.loger.info(threading.current_thread().getName() + " start")
        crawl_faild_time = 0
        while crawl_faild_time < 3:
            try:
                urldata = self.urls.get(timeout=10)
            except Exception as e:
                self.loger.exception('got get url from queue timeout')
                crawl_faild_time += 1
                continue

            url, depth, failed_time = urldata
            if failed_time > 3:
                self.loger.warning("the url:%s faild to mush time,throw out" % (url))
                continue
            if depth > int(self.conf["max_depth"]):
                self.loger.info("the depth:%d is over the max_depth:%d, crawl end" % \
                                (depth, int(self.conf["max_depth"])))
                break

            print(urldata)
            try:
                self.loger.info("start crawl url:%s" % (url))
                html = self.wget(url)

                pattern = self.conf["target_url"]
                if re.match(pattern, url) and self.download(url, html):
                    continue

                for link in self.find_links(url, html):
                    self.urls.put((link, depth + 1, 0))
            except Exception as e:
                self.loger.exception('Got exception on crawl thread')
                self.urls.put((url, depth, failed_time + 1))
            finally:
                time.sleep(int(self.conf["crawl_interval"]))

        self.loger.info(threading.current_thread().getName() + " is end")


    def download(self, link, html):
        """
        Download the html of target link to local disk.

        Args:
            link: A str of the target link.
            html: The html data of the target link.
        Returns:
            bool: The bool value of whether the html data already downloaf.
        """
        file_path = self.conf["output_directory"] + "/" + link.replace(r"/", r"\\")
        if (os.path.exists(file_path)):
            self.loger.info("%s is already download" % (file_path))
            return True
        print(link)
        with open(file_path, "wb") as file:
            file.write(html)
        return False

    def start(self):
        """
        Start all the thread of the mini_spider to crawl the target link.

        """
        self.loger.info("start spider")
        for thread in self.threads:
            thread.start()
        for i, thread in enumerate(self.threads):
            thread.join()
        self.loger.info("crawl task is done.program exit.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", help="show the version of mini_spider.py", action="store_true")
    parser.add_argument("-c", "--conf", help="provide spider conf files path to script", type=str)
    args = parser.parse_args()

    if args.v:
        print("version of mini_spider.py is 0.0.1")
    elif args.conf:
        MiniSpider(args.conf).start()
