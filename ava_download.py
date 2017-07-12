# coding: utf-8
import urllib2
from bs4 import BeautifulSoup
import urllib
import logging
import time
import requests
import os
import random

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m-%d %H:%M')

class WebParser(object):
    def __init__(self, wait_second=1, max_retry_time=10):
        self.html_cache_path = "./data/html_cache/"
        self.img_path = "./data/img_cache/"
        self.soup = None
        self.wait_second = wait_second
        self.max_retry_time = max_retry_time
    
    def build_request_url(self, imgid):
        url_pattern = "http://www.dpchallenge.com/image.php?IMAGE_ID=%s"
        return url_pattern%imgid
    
    def build_request_headers(self):
        user_agent = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.24) Gecko/20111109 CentOS/3.6.24-3.el6.centos Firefox/3.6.24"
        request_headers = {'User-Agent': user_agent}
        return request_headers

    def load_html(self, imgid):
        cache_file = self.html_cache_path + "%s.html"%imgid
        if os.path.exists(cache_file):
            logging.info("[imgid=%s]html has been cached."%imgid)
            html = open(cache_file, 'r').read()
        else:
            url = self.build_request_url(imgid)
            headers = self.build_request_headers()
            is_opened = False
            for _ in range(self.max_retry_time):
                try:
                    html = requests.get(url=url, headers=headers).content
                except Exception, e:
                    logging.error(str(e))
                else:
                    self.save_html(html, cache_file)
                    logging.info("[imgid=%s]download html successfully."%imgid)
                    is_opened = True
                    break
                finally:
                    time.sleep(self.wait_second)
            if not is_opened:
                logging.warning("[imgid=%s]download html failed."%imgid)
                return False
        self.soup = BeautifulSoup(html, 'html.parser')
        return True

    def save_html(self, html, cache_file):
        fhtml = open(cache_file, 'w')
        fhtml.write(html)
        fhtml.close()

    def save_image(self, imgid):
        cached_img = self.img_path + "%s.jpg"%imgid
        if os.path.exists(cached_img):
            logging.info("[imgid=%s]image has been cached."%imgid)
        else:
            img_url = self.get_img_url()
            if img_url is None:
                logging.warning("[imgid=%s]image does not exist."%imgid)
                return False
            try:
                urllib.urlretrieve(img_url, cached_img)
            except Exception, e:
                logging.warning("[imgid=%s]image caches failed."%imgid)
                return False
            else:
                logging.info("[imgid=%s]image caches successfully."%imgid)
        return True

    def get_img_url(self):
        img_container = self.soup.find("td", id="img_container")
        if img_container is None or len(img_container.contents) < 2:
            return None
        else:
            return img_container.contents[1].get("src", None)


web_parser = WebParser(wait_second=1, max_retry_time=5)

with open("./data/ava/AVA.txt", 'r') as fin:
    for i, line in enumerate(fin):
        fields = line.strip().split(" ")
        imgid = fields[1]
        if web_parser.load_html(imgid):
            web_parser.save_image(imgid)

